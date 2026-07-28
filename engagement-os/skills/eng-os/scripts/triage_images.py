#!/usr/bin/env python3
"""Make image triage executable: gather the evidence, then apply the verdicts.

`convert_source.py` extracts every image it cannot prove decorative and tags it `[uncertain]`.
Deciding which of those carry information is a vision + judgment task, and the skills said so —
but saying so was all they did. Facing 34 images in one deck (296 in another), the cheapest
action that clears the lint is to call them all `[decorative]` and delete them, which is exactly
what happened to the AIB deck: 13 extracted, 13 deleted, including the architecture diagram the
whole case study rests on. This script removes that pressure from both ends.

    --worklist   one record per `[uncertain]` image: where it sits, how big it is, what OCR
                 found, and the markdown around it. That is what a vision pass needs in order
                 to judge; without it triage means opening files one at a time and guessing.
    --apply      the mechanical half — delete a decorative file with its inline block and its
                 index line, write a real caption over a `[caption-needed]` stub, park OCR text
                 in a collapsible block — plus a ledger row per verdict. 296 images of that by
                 hand is where errors get in.

The judgment stays with the agent. This script does not classify: it has no view on whether a
364x231 PNG is an icon or an architecture diagram, and neither does OCR — tesseract read ZERO
words off the AIB as-is architecture diagram, so an OCR-only filter would have deleted it too.
Only vision decides, which is why `--worklist` exists to feed one and `--apply` to record it.

Usage:
    python triage_images.py --worklist <md_path> [--json]
    python triage_images.py --apply <md_path> --verdicts <verdicts.json>

Verdicts file: a JSON list, one object per image.
    {"image": "<filename>", "verdict": "content",    "caption": "what it shows, in the words
                                                                 of the surrounding clause"}
    {"image": "<filename>", "verdict": "decorative", "reason": "line icon — rosette in hands"}
    {"image": "<filename>", "verdict": "ocr-done",   "caption": "...", "ocr": "verbatim text"}
Every `[uncertain]` image must appear exactly once; a missing one is refused rather than
silently left behind, because "we forgot it" and "we judged it" must not look the same.

OCR in the worklist uses `tesseract` when installed. It is a hint for the vision pass — a strong
positive signal (this figure carries text) and a worthless negative one (small type reads as
nothing). Missing tesseract degrades the hint, never the pass.
"""
import argparse
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figure_contract as fc

CONTEXT_CHARS = 400          # markdown either side of the figure — enough to caption from
OCR_CHARS = 20_000           # JSON also feeds the transcript; do not cut maps/tables at 600 chars
DUPLICATE_OVERLAP = 0.80     # above this the image's words are already in the page's prose
MIN_CAPTION_CHARS = 60       # below this the caption names the figure instead of explaining it

UNCERTAIN_RE = fc.INDEX_UNTRIAGED
LEDGER_HEAD = fc.LEDGER_LINE
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9&/-]{3,}")


def _tokens(s):
    return {w.lower() for w in _WORD_RE.findall(s or "")}


def _unit_prose(text, unit):
    """The prose the extractor already pulled off this page/slide, figures removed.

    Comparing an image's words against this answers the one question the triage rule turns on
    and no one could previously answer: did this figure's text survive extraction? A slide's
    table renders as vector shapes, so it becomes a page snapshot — but pymupdf usually read
    that table's text perfectly well, and transcribing it again adds nothing. Measured on the
    AIB deck: 14 of 18 OCR blocks were 95-100% words the markdown already had, three of them
    word-for-word duplicates.
    """
    if not unit:
        return ""
    m = re.search(r"(?m)^## " + re.escape(unit) + r":?\s*$", text)
    if not m:
        return ""
    nxt = re.search(r"(?m)^## |^---\n", text[m.end():])
    body = text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]
    body = re.sub(r"<details>.*?</details>", " ", body, flags=re.S)
    body = re.sub(r"\*Figure `.*?`.*?\*", " ", body, flags=re.S)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
    return body


def _overlap(image_text, prose):
    """Share of the image's words that the extracted prose already contains."""
    a = _tokens(image_text)
    if not a:
        return None
    return round(len(a & _tokens(prose)) / len(a), 2)


_inline_block_re = fc.stub_block_re
_index_line_re = fc.index_line_re


def _ocr(path):
    from shutil import which
    if not which("tesseract"):
        return None
    import subprocess
    try:
        # Leptonica/Tesseract builds on macOS can fail to open an otherwise readable absolute
        # path (observed on the real IDO worklist: 122/122 OCR hints silently became None) while
        # the identical file succeeds from its parent directory. Run against the basename with
        # an explicit cwd; it is also shorter and avoids shell/path quoting entirely.
        path = pathlib.Path(path).resolve()
        r = subprocess.run(["tesseract", path.name, "-"], cwd=str(path.parent),
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            return None
        # Keep line boundaries: maps, matrices and process diagrams use them to separate
        # labels. Flattening all whitespace made the JSON evidence much harder to interpret
        # and turned the supposedly verbatim OCR block into an unstructured paragraph.
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in r.stdout.splitlines()]
        return "\n".join(line for line in lines if line).strip()[:OCR_CHARS]
    except Exception:
        return None


def _dims(path):
    """Width/height without a hard Pillow dependency — read the PNG/JPEG header."""
    try:
        with open(path, "rb") as f:
            head = f.read(32)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            import struct
            w, h = struct.unpack(">II", head[16:24])
            return w, h
    except Exception:
        pass
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.width, im.height
    except Exception:
        return None, None


def _unit_for(text, pos):
    """The `## Page N:` / `## Slide N:` heading the figure sits under — its citation anchor."""
    heads = list(re.finditer(r"(?m)^## (Page|Slide|Sheet|Section)[^\n]*$", text[:pos]))
    return heads[-1].group(0).strip("# ").rstrip(":") if heads else None


def worklist(md_path):
    """One record per `[uncertain]` image, in document order."""
    md = pathlib.Path(md_path)
    text = md.read_text(encoding="utf-8", errors="replace")
    items = []
    for m in UNCERTAIN_RE.finditer(text):
        rel = m.group(1)
        path = md.parent / rel
        # where the figure was PLACED, not where the index lists it — the index sits at the
        # end of the file, and a caption written from the end of the file is a caption
        # written from nothing.
        placed = re.search(r"!\[[^\]]*\]\(" + re.escape(rel) + r"\)", text)
        pos = placed.start() if placed else m.start()
        w, h = _dims(path)
        unit = _unit_for(text, pos)
        ocr = _ocr(path) if path.exists() else None
        overlap = _overlap(ocr, _unit_prose(text, unit))
        items.append({
            "image": os.path.basename(rel),
            "path": str(path),
            "rel": rel,
            "unit": unit,
            "width": w, "height": h,
            "kb": round(path.stat().st_size / 1024, 1) if path.exists() else None,
            "ocr": ocr,
            # how much of what this figure says the markdown ALREADY says. High → transcribing
            # it again is noise; caption what the words cannot carry (the structure) instead.
            "text_already_in_md": overlap,
            "verdict_hint": ("explain the structure — its words are already in the page prose"
                             if overlap is not None and overlap >= DUPLICATE_OVERLAP
                             else "its words are NOT in the page prose — capture them"),
            "context": text[max(0, pos - CONTEXT_CHARS):pos + CONTEXT_CHARS].strip(),
        })
    return items


def _caption(rel, body):
    """Just the caption line — the image itself is re-emitted by the caller."""
    return fc.placed_figure(rel, body.strip()).split("\n\n", 1)[1]


def apply_verdicts(md_path, verdicts):
    """Rewrite the markdown to match the verdicts. Returns a per-verdict tally.

    Refuses a partial pass. An image the agent never looked at and an image it judged must not
    end up in the same state, or the ledger records a decision nobody made.
    """
    md = pathlib.Path(md_path)
    text = md.read_text(encoding="utf-8", errors="replace")
    by_name = {}
    for m in UNCERTAIN_RE.finditer(text):
        by_name[os.path.basename(m.group(1))] = m.group(1)

    given = {v["image"] for v in verdicts}
    missing = set(by_name) - given
    unknown = given - set(by_name)
    if missing:
        raise SystemExit(f"ERROR: {len(missing)} `[uncertain]` image(s) have no verdict — "
                         f"judge every one or none: {', '.join(sorted(missing)[:5])}"
                         + (" …" if len(missing) > 5 else ""))
    if unknown:
        raise SystemExit(f"ERROR: verdict given for image(s) not awaiting triage in this file: "
                         f"{', '.join(sorted(unknown)[:5])}")

    tally = {"content": 0, "decorative": 0, "ocr-done": 0}
    ledger = []
    for v in verdicts:
        name, kind = v["image"], v["verdict"]
        rel = by_name[name]
        if kind not in fc.VERDICTS:
            raise SystemExit(f"ERROR: unknown verdict '{kind}' for {name} — use "
                             + " / ".join(fc.VERDICTS))

        if kind == "decorative":
            reason = (v.get("reason") or "").strip()
            if not reason:
                # Deleting an image is the one irreversible verdict, and the failure this
                # script exists to prevent was a silent bulk delete. A reason costs a phrase
                # and makes the pass reviewable.
                raise SystemExit(f"ERROR: {name} marked decorative with no reason — say what "
                                 "it is (logo / icon / background / rule / spacer)")
            text = _inline_block_re(rel).sub("\n\n", text)
            text = _index_line_re(rel).sub("", text)
            p = md.parent / rel
            if p.exists():
                p.unlink()
            ledger.append(f"`{name}` decorative — {reason}")
        else:
            caption = (v.get("caption") or "").strip()
            # The caption is not a label, it is the deliverable: downstream reads the markdown
            # and must not have to open the image. "Figure 3" or the filename back again tells
            # a reader nothing, and passes every check that only tests for non-empty.
            if len(caption) < MIN_CAPTION_CHARS or _tokens(caption) <= _tokens(name):
                raise SystemExit(
                    f"ERROR: {name} kept as {kind} with no real caption — a reader of this "
                    "markdown must learn what the figure says without opening it. Describe "
                    "what it shows (the boxes, the flow, the axis, the rows), not what it is "
                    f"called. Got: {caption!r}")
            block = _caption(rel, caption)
            if kind == "ocr-done":
                ocr = (v.get("ocr") or "").strip()
                if not ocr:
                    raise SystemExit(f"ERROR: {name} tagged ocr-done with no OCR text — an "
                                     "`[uncertain]` figure's text must be captured, not skipped")
                # `ocr-done` means "this figure's text did not survive extraction". When it
                # plainly did, transcribing it a second time buries the page in noise and
                # buries the interpretation with it.
                dup = _overlap(ocr, _unit_prose(text, _unit_for(text, text.find(rel))))
                if dup is not None and dup >= DUPLICATE_OVERLAP:
                    raise SystemExit(
                        f"ERROR: {name} tagged ocr-done but {dup:.0%} of that text is already "
                        "in this page's extracted prose — re-transcribing it adds nothing. Use "
                        "`content` and caption what the words cannot carry: which box feeds "
                        "which, the swimlanes, the axis, what the figure argues.")
                block += (f"\n<details><summary>OCR extracted text — {name}</summary>\n\n"
                          f"{ocr}\n\n</details>\n")
            # the stub's own trailing blank lines were consumed with it; restore one so the
            # figure does not fuse with the clause that follows it
            text = _inline_block_re(rel).sub("\n![%s](%s)\n\n%s\n" % (name, rel, block), text)
            text = _index_line_re(rel).sub(f"- `[{kind}]` ![{name}]({rel})\n", text)
        tally[kind] += 1

    text = _write_ledger(text, tally, ledger)
    md.write_text(text, encoding="utf-8")
    return tally


TRIAGED_HEAD = fc.HEADING_DONE + "\n"


def _write_ledger(text, tally, ledger):
    """Record what was decided, inside the file the decision was about.

    Without this a document whose images were all deleted is indistinguishable from a document
    that never had any — which is how 13 lost diagrams left no trace. `eng_lint` reconciles
    this against the extracted count in the header.

    The converter's heading and its "classify each …" instructions describe work still to do;
    `--apply` refuses a partial pass, so once it returns that work is done and leaving the
    instructions there tells the next reader to redo it.
    """
    lines = [f"\n{LEDGER_HEAD} {tally['content']} content · {tally['ocr-done']} ocr-done · "
             f"{tally['decorative']} decorative (deleted). Every extracted image was judged; "
             "each surviving figure is placed inline at the position it held in the source.\n"]
    if ledger:
        lines += ["\nDeleted as decorative:\n"] + [f"- {row}" for row in ledger]
    block = "\n".join(lines).rstrip("\n") + "\n\n"
    # re-triage: replace the previous ledger, don't stack a second one
    text = fc.LEDGER_BLOCK.sub("", text)

    # Swap the heading and drop the "classify each …" instructions, which describe work that
    # --apply has just finished — but KEEP the converter's two accounting lines: how many
    # images it extracted, and how many it auto-dropped before triage ever saw them. Those
    # are what `eng_lint.rule_images_accounted` reconciles the ledger against.
    head = re.search(r"(?m)^(?:" + re.escape(fc.HEADING_PENDING) + r"|" +
                     re.escape(fc.HEADING_DONE) + r")\n"
                     r"(?:(?!^- `\[|^## ).*\n)*", text)
    if not head:
        return text.rstrip("\n") + "\n\n---\n\n" + TRIAGED_HEAD + block
    kept = [ln for ln in head.group(0).splitlines()[1:]
            if ln.startswith(fc.PRESERVED_LINES)]
    preserved = ("\n" + "\n".join(kept) + "\n") if kept else ""
    return text[:head.start()] + TRIAGED_HEAD + preserved + block + text[head.end():]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worklist", metavar="MD", help="emit the evidence a vision pass needs")
    ap.add_argument("--apply", metavar="MD", help="apply verdicts to this markdown")
    ap.add_argument("--verdicts", metavar="JSON", help="verdicts file for --apply")
    ap.add_argument("--json", action="store_true", help="machine-readable worklist")
    args = ap.parse_args()

    if args.worklist:
        items = worklist(args.worklist)
        if args.json:
            print(json.dumps(items, indent=2, ensure_ascii=False))
            return 0
        if not items:
            print("  nothing awaiting triage — every extracted image has been judged")
            return 0
        print(f"  {len(items)} image(s) awaiting triage in {os.path.basename(args.worklist)}\n")
        for it in items:
            size = (f"{it['width']}x{it['height']}" if it["width"] else "?") + f", {it['kb']}KB"
            print(f"  {it['image']}\n      at: {it['unit'] or '—'} · {size}\n      path: {it['path']}")
            if it["text_already_in_md"] is not None:
                print(f"      text already in the md: {it['text_already_in_md']:.0%}"
                      f" — {it['verdict_hint']}")
            if it["ocr"]:
                print(f"      ocr: {re.sub(r'\\s+', ' ', it['ocr'])[:160]}")
            print()
        print("  → look at each one (Read renders it), then --apply a verdicts file.")
        return 0

    if args.apply:
        if not args.verdicts:
            ap.error("--apply needs --verdicts")
        verdicts = json.loads(pathlib.Path(args.verdicts).read_text(encoding="utf-8"))
        tally = apply_verdicts(args.apply, verdicts)
        print(f"Triaged {os.path.basename(args.apply)}: "
              f"{tally['content']} content, {tally['ocr-done']} ocr-done, "
              f"{tally['decorative']} decorative (deleted).")
        return 0

    ap.error("give --worklist or --apply")


if __name__ == "__main__":
    sys.exit(main())
