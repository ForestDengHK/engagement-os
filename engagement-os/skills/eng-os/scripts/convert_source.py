#!/usr/bin/env python3
"""Convert one source document to faithful, citable Markdown for the reference pack.

Deterministic extraction only: text + tables with per-page/slide anchors, plus image
extraction to a sibling images dir.

Images that are decorative *by construction* are dropped here rather than pushed onto the agent:
a raster repeated across pages/slides is template furniture (logo, footer mark, divider) and one
under a few KB is an icon or rule. Both are counted and reported in the output, so the pass stays
auditable. Everything that survives is tagged `[uncertain]` for the agent to classify
[decorative]/[content] and OCR — that part is a judgment + vision task. See `eng-ingest-source`.

EXTRACTION IS DELEGATED, NOT REIMPLEMENTED. docx goes through `pandoc` and pptx through
`markitdown` — the same tools the `docx` / `pptx` skills read with. They settled document order,
heading levels, lists, footnotes, nested tables and shape coverage years ago; hand-rolling that
on top of python-docx/python-pptx just reproduces their bugs. pdf stays on pymupdf and xlsx on
openpyxl because those need per-page / per-sheet control to place the anchors, which a
whole-file converter cannot give.

What this script owns is the PACKAGING the pack's discipline depends on and no general converter
provides: the provenance header (source path, md5, unit counts), the citable anchor per unit,
image extraction to disk with decorative auto-drop, and one uniform interface across six formats.
Each output names its extractor, and a fallback says plainly what it lost.

Still reach for the matching SKILL, per document, when the script's own output falls short:
tracked changes, comments, chart data labels, or a scanned PDF needing real OCR.

Usage:
    python convert_source.py <source_path> [--out <md_path>] [--images-dir <dir>]

Supported: .pdf .pptx .ppsx .docx .xlsx .csv .png .jpg .jpeg
Dependencies are imported lazily; a missing one degrades that format with a clear message
rather than crashing. Install as needed: pip install pymupdf python-pptx python-docx openpyxl
(PEP-668/Homebrew Python: add --user --break-system-packages, or use a venv.)
"""
import argparse
import hashlib
import os
import pathlib
import re
import sys
import datetime as _dt


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def header(src, extra=""):
    return (
        f"# {os.path.basename(src)}\n\n"
        f"> **Source:** `{src}`  \n"
        f"> **Converted:** {_dt.date.today().isoformat()}  \n"
        f"> **md5:** `{md5(src)}`  \n"
        f"{extra}\n---\n\n"
    )


MIN_IMG_BYTES = 6 * 1024        # below this is an icon, bullet, rule or spacer
MIN_IMG_PIXELS = 120            # narrowest side; logos and dividers fall under this


class ImageCollector:
    """Collects extracted images, dropping the ones that are decorative by construction.

    Two heuristics do almost all the work, and both are decidable from the bytes:

    * **Repeats.** A raster that appears on more than one page/slide is template furniture —
      a logo, a footer mark, a divider. Content diagrams do not repeat. This is the strong one.
    * **Size.** Under a few KB, or narrower than ~120px, it is an icon or a rule.

    Everything dropped is counted and reported, so the pass stays auditable: the lossless rule
    is about not losing *information*, and a logo carries none. What survives is what a human
    would actually have to look at.
    """

    def __init__(self, images_dir):
        self.dir = images_dir
        self.kept = []                  # (relpath, unit) in emit order
        self._by_digest = {}            # digest -> [(path, unit), ...]
        self.dropped_small = 0

    def add(self, blob, unit, name):
        """Offer one image. Returns True if written to disk."""
        if len(blob) < MIN_IMG_BYTES:
            self.dropped_small += 1
            return False
        digest = hashlib.md5(blob).hexdigest()
        path = os.path.join(self.dir, name)
        os.makedirs(self.dir, exist_ok=True)
        with open(path, "wb") as f:
            f.write(blob)
        rel = os.path.relpath(path, os.path.dirname(self.dir))
        self._by_digest.setdefault(digest, []).append((path, rel, unit))
        return True

    def finalise(self):
        """Delete repeats, keep one copy of anything unique. Returns (kept, dropped_repeat)."""
        dropped_repeat = 0
        for copies in self._by_digest.values():
            if len(copies) > 1:                      # same bytes on 2+ units → template furniture
                for path, _rel, _unit in copies:
                    try:
                        os.remove(path)
                    except OSError:
                        pass
                    dropped_repeat += 1
            else:
                _path, rel, unit = copies[0]
                self.kept.append((rel, unit))
        self.kept.sort(key=lambda t: t[1])
        return self.kept, dropped_repeat


def img_section(collector):
    if isinstance(collector, list):                  # legacy call-site safety
        kept, dropped_repeat, dropped_small = [(i, 0) for i in collector], 0, 0
    else:
        kept, dropped_repeat = collector.finalise()
        dropped_small = collector.dropped_small
    note = ""
    if dropped_repeat or dropped_small:
        bits = []
        if dropped_repeat:
            bits.append(f"{dropped_repeat} repeated across units (logo / template furniture)")
        if dropped_small:
            bits.append(f"{dropped_small} under {MIN_IMG_BYTES // 1024}KB (icon / rule / spacer)")
        note = f"\n**Auto-dropped as decorative:** {' · '.join(bits)}. " \
               "Repeats and icons carry no information; nothing that appears once was touched.\n"
    if not kept:
        return ("\n---\n\n## Images\n" + note + "\nNo content-bearing images.\n") if note else ""
    lines = ["\n---\n\n## Images extracted — triage these\n", note,
             "Classify each `[decorative]` (delete) / `[content]` (keep + caption) / "
             "`[uncertain]` (OCR inline, then retag `[ocr-done]`). Do not delete an "
             "`[uncertain]` image before its text is captured.\n"]
    for im, _unit in kept:
        lines.append(f"- `[uncertain]` ![{os.path.basename(im)}]({im})")
    return "\n".join(lines) + "\n"


def _tool(name):
    """Path to an external converter, or None."""
    from shutil import which
    return which(name)


def _run(cmd):
    import subprocess
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        return r.stdout if r.returncode == 0 and r.stdout.strip() else None
    except Exception:
        return None


def number_headings(md, label="Section"):
    """Give every markdown heading a stable, citable number, keeping its level.

    The extraction tools return the document's real heading hierarchy; what they can't give is
    an anchor a downstream claim can cite. Numbering in place adds one without flattening the
    structure: `## Minimum Requirements` becomes `## Section 12: Minimum Requirements`, so
    `file.md §Section 12` resolves and the outline still reads as an outline.
    """
    out, n = [], 0
    for line in md.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m and m.group(2).strip():
            n += 1
            out.append(f"{m.group(1)} {label} {n}: {m.group(2).strip()}")
        else:
            out.append(line)
    return "\n".join(out), n


def _pptx_shapes(container):
    """Yield shapes depth-first: a grouped diagram keeps its labels in child shapes, and
    `slide.shapes` only yields the top level — those labels would be lost silently."""
    for sh in container:
        if getattr(sh, "shape_type", None) == 6:      # GROUP
            yield from _pptx_shapes(sh.shapes)
        else:
            yield sh


def convert_pdf(src, images_dir):
    try:
        import fitz  # pymupdf
    except ImportError:
        return None, "pymupdf not installed — run: pip install pymupdf (PEP-668: add --user --break-system-packages)"
    doc = fitz.open(src)
    out = [header(src, f"> **Pages:** {doc.page_count}  ")]
    coll = ImageCollector(images_dir)
    for i, page in enumerate(doc, 1):
        out.append(f"## Page {i}:\n")
        text = page.get_text("text").strip()
        out.append(text + "\n" if text else "_(no extractable text — likely a diagram/image page; see extracted images)_\n")
        for j, img in enumerate(page.get_images(full=True)):
            try:
                pix = fitz.Pixmap(doc, img[0])
                if pix.n - pix.alpha >= 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                if min(pix.width, pix.height) < MIN_IMG_PIXELS:
                    coll.dropped_small += 1
                    continue
                coll.add(pix.tobytes("png"), i, f"p{i}_img{j}.png")
            except Exception:
                continue
    return "\n".join(out) + img_section(coll), None


def convert_pptx(src, images_dir):
    try:
        from pptx import Presentation
    except ImportError:
        return None, "python-pptx not installed — run: pip install python-pptx (PEP-668: add --user --break-system-packages)"
    prs = Presentation(src)
    coll = ImageCollector(images_dir)

    # markitdown owns the text: it reaches shape types python-pptx makes you hunt for and
    # carries each picture's embedded accessibility description, which is often the only
    # written account of a diagram. python-pptx still does the image FILES — markitdown
    # names images but does not write them, and the pack needs them on disk for triage.
    if _tool("markitdown"):
        md = _run(["markitdown", src])
        if md:
            body = re.sub(r"<!--\s*Slide number:\s*(\d+)\s*-->", r"## Slide \1:", md)
            for i, slide in enumerate(prs.slides, 1):
                for shape in _pptx_shapes(slide.shapes):
                    if getattr(shape, "shape_type", None) == 13:
                        try:
                            coll.add(shape.image.blob, i, f"s{i}_{shape.shape_id}.{shape.image.ext}")
                        except Exception:
                            continue
            head = header(src, f"> **Slides:** {len(prs.slides)}  \n> **Extractor:** markitdown  ")
            return head + body + img_section(coll), None

    out = [header(src, f"> **Slides:** {len(prs.slides)}  \n> **Extractor:** python-pptx (fallback — install markitdown for richer shape coverage + image alt-text)  ")]
    for i, slide in enumerate(prs.slides, 1):
        out.append(f"## Slide {i}:\n")
        for shape in _pptx_shapes(slide.shapes):
            if shape.has_text_frame and shape.text_frame.text.strip():
                out.append(shape.text_frame.text.strip() + "\n")
            if shape.has_table:
                tbl = shape.table
                rows = [[c.text.strip() for c in r.cells] for r in tbl.rows]
                if rows:
                    out.append("| " + " | ".join(rows[0]) + " |")
                    out.append("| " + " | ".join("---" for _ in rows[0]) + " |")
                    for r in rows[1:]:
                        out.append("| " + " | ".join(r) + " |")
                    out.append("")
            if shape.shape_type == 13:  # picture
                try:
                    image = shape.image
                    coll.add(image.blob, i, f"s{i}_{shape.shape_id}.{image.ext}")
                except Exception:
                    continue
        try:
            if slide.has_notes_slide:
                notes = slide.notes_slide.notes_text_frame.text.strip()
                if notes:
                    out.append(f"**Speaker notes:**\n\n{notes}\n")
        except Exception:
            pass
    return "\n".join(out) + img_section(coll), None


def convert_docx(src, images_dir):
    # Pandoc owns the extraction. It keeps document order (tables stay in their clause), real
    # heading levels, lists, footnotes and nested tables — all things a hand-rolled python-docx
    # walk gets wrong, and all things pandoc settled years ago. We add only what pandoc has no
    # reason to know about: the provenance header and the citable section numbering.
    if _tool("pandoc"):
        # --extract-media makes pandoc write the embedded images out; without it a docx's
        # diagrams are silently dropped, which no amount of good text extraction makes up for.
        # Pandoc has no view on which of them matter, so its output goes through the same
        # decorative filter as every other format.
        import shutil
        import tempfile
        tmp = tempfile.mkdtemp(prefix="engos-media-")
        md = _run(["pandoc", "-t", "gfm", "--wrap=none", f"--extract-media={tmp}", src])
        if md:
            coll = ImageCollector(images_dir)
            for root, _dirs, files in os.walk(tmp):
                for fn in sorted(files):
                    src_img = os.path.join(root, fn)
                    try:
                        with open(src_img, "rb") as fh:
                            coll.add(fh.read(), fn, fn)
                    except OSError:
                        continue
            shutil.rmtree(tmp, ignore_errors=True)
            # pandoc points at its own temp dir; repoint at the pack's images dir, and drop
            # the links to images the filter removed so the markdown has no dead references.
            kept_names = {os.path.basename(rel) for rel, _u in coll.kept}
            rel_dir = os.path.basename(images_dir.rstrip("/"))

            def _fix(m):
                name = os.path.basename(m.group(2))
                return f"![{m.group(1)}]({rel_dir}/{name})" if name in kept_names else ""
            md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _fix, md)
            body, n = number_headings(md, "Section")
            head = header(src, f"> **Sections:** {n}  \n> **Extractor:** pandoc  ")
            return head + body + img_section(coll), None

    # Fallback: no pandoc on this machine. Order is lost (python-docx exposes paragraphs and
    # tables as two separate sequences) — the header says so rather than pretending otherwise.
    try:
        import docx  # python-docx
    except ImportError:
        return None, "no pandoc, and python-docx not installed — install either: brew install pandoc | pip install python-docx (PEP-668: add --user --break-system-packages)"
    d = docx.Document(src)
    # A .docx has no stable page concept — pagination is decided by the renderer, so a "page"
    # anchor would not survive a font change. Anchor on SECTIONS instead (headings, or one
    # implicit section for a heading-less doc) so a claim is still citable as `file.md §Section N`.
    body, section, n = [], [], 0
    for para in d.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        if "heading" in (para.style.name or "").lower():
            if section:
                body.append("\n".join(section))
            n += 1
            section = [f"## Section {n}: {text}\n"]
        else:
            if not section:                       # text before the first heading
                n += 1
                section = [f"## Section {n}:\n"]
            section.append(text + "\n")
    if section:
        body.append("\n".join(section))

    out = [header(src, f"> **Sections:** {n}  \n> **Extractor:** python-docx (fallback — tables are appended after the text, not in document order; install pandoc for faithful order)  ")]
    out.extend(body)
    for t, table in enumerate(d.tables, 1):
        rows = [[c.text.strip() for c in r.cells] for r in table.rows]
        if rows:
            out.append(f"\n**Table {t}:**\n")
            out.append("| " + " | ".join(rows[0]) + " |")
            out.append("| " + " | ".join("---" for _ in rows[0]) + " |")
            for r in rows[1:]:
                out.append("| " + " | ".join(r) + " |")
            out.append("")
    return "\n".join(out), None


def convert_xlsx(src, images_dir):
    try:
        import openpyxl
    except ImportError:
        return None, "openpyxl not installed — run: pip install openpyxl (or use the xlsx skill; PEP-668: add --user --break-system-packages)"
    wb = openpyxl.load_workbook(src, data_only=True, read_only=True)
    out = [header(src, f"> **Sheets:** {len(wb.sheetnames)}  ")]
    for name in wb.sheetnames:
        ws = wb[name]
        out.append(f"## Sheet: {name}\n")
        rows = list(ws.iter_rows(values_only=True))
        rows = [r for r in rows if any(c is not None for c in r)]
        if not rows:
            out.append("_(empty)_\n")
            continue
        width = max(len(r) for r in rows)
        def cell(x):
            return "" if x is None else str(x).replace("|", "\\|").replace("\n", " ")
        out.append("| " + " | ".join(cell(c) for c in (list(rows[0]) + [""] * (width - len(rows[0])))) + " |")
        out.append("| " + " | ".join("---" for _ in range(width)) + " |")
        for r in rows[1:]:
            padded = list(r) + [""] * (width - len(r))
            out.append("| " + " | ".join(cell(c) for c in padded) + " |")
        out.append("")
    return "\n".join(out), None


def convert_csv(src, images_dir):
    import csv
    out = [header(src)]
    with open(src, newline="", encoding="utf-8", errors="replace") as f:
        rows = list(csv.reader(f))
    rows = [r for r in rows if any(c.strip() for c in r)]
    if rows:
        out.append("| " + " | ".join(rows[0]) + " |")
        out.append("| " + " | ".join("---" for _ in rows[0]) + " |")
        for r in rows[1:]:
            out.append("| " + " | ".join(r) + " |")
    return "\n".join(out), None


def convert_image(src, images_dir):
    rel = os.path.relpath(src, os.path.dirname(images_dir)) if images_dir else src
    body = header(src) + (
        f"## Image\n\n`[uncertain]` ![{os.path.basename(src)}]({rel})\n\n"
        "_This is an image source — OCR it inline (agent + vision), then retag `[ocr-done]`._\n"
    )
    return body, None


DISPATCH = {
    ".pdf": convert_pdf, ".pptx": convert_pptx, ".ppsx": convert_pptx,
    ".docx": convert_docx, ".xlsx": convert_xlsx, ".csv": convert_csv,
    ".png": convert_image, ".jpg": convert_image, ".jpeg": convert_image,
}


ASSET_KINDS = ("approaches", "case_studies", "cvs", "credentials", "diagrams", "finance")


def scan(root):
    """What showed up in the tree that hasn't been dealt with yet.

    Asking the user to type a path for every arriving document is asking them to do what a
    directory listing can decide. Two kinds of "not dealt with", because the two kinds of
    material have different destinations:

      INGEST — sourced material (given to us or found by us, plus the tender pack). Un-ingested
        when nothing named after it exists under the matching `_md/`. Needs no manifest.
      INDEX  — our OWN reusable assets under `01_pursuit/_shared/<kind>/`. These are never
        converted and never bucketed; they belong in `firm_assets.md`, and one that has no row
        there is invisible to the bid — which is how the only sector-matching case study in a
        pack turns out to be undated on submission week.

    Returns (to_ingest, to_index), each [(area_label, path)].
    """
    to_ingest = []
    areas = [(p, p / "_md") for p in root.glob("_sources/*") if p.is_dir()]
    areas += [(p, p / "_md") for p in root.glob("01_pursuit/*/1_received") if p.is_dir()]
    for area, md_dir in areas:
        converted = {p.stem.lower() for p in md_dir.rglob("*.md")} if md_dir.exists() else set()
        for src in sorted(area.rglob("*")):
            if not src.is_file() or src.suffix.lower() not in DISPATCH:
                continue
            if md_dir in src.parents:            # already inside _md/ — an extracted image
                continue
            if src.stem.lower() not in converted:
                to_ingest.append((str(area.relative_to(root)), src))

    to_index = []
    for shared in root.glob("01_pursuit/_shared"):
        index_file = shared / "firm_assets.md"
        indexed = index_file.read_text(encoding="utf-8", errors="replace") if index_file.exists() else ""
        # Walk ALL of _shared/, not a whitelist of kinds. The scaffold plants six, and the
        # folder's own README tells the user to add a new one rather than force a bad fit —
        # so a whitelist makes exactly the assets someone thought about hardest invisible.
        for asset in sorted(shared.rglob("*")):
            if not asset.is_file() or asset.name.startswith("."):
                continue
            if asset.parent.name == "_md" or (shared / "_md") in asset.parents:
                continue                          # conversions, not assets
            if asset.name in ("README.md", "firm_assets.md"):
                continue
            # any file type — a rate card or a CV is an asset whether or not we can convert it
            if asset.name not in indexed:
                where = asset.parent.relative_to(root)
                to_index.append((str(where), asset))
    return to_ingest, to_index


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", nargs="?",
                    help="the document to convert. Omit it with --scan to find what is waiting.")
    ap.add_argument("--scan", metavar="ROOT", nargs="?", const=".",
                    help="list source files in the engagement tree with no markdown yet, "
                         "and exit. Answers 'what arrived that I haven't ingested?'")
    ap.add_argument("--out", help="output .md path (default: source with .md next to it)")
    ap.add_argument("--images-dir", help="dir for extracted images (default: <out_dir>/images)")
    args = ap.parse_args()

    if args.scan is not None:
        root = pathlib.Path(args.scan).resolve()
        to_ingest, to_index = scan(root)
        if not to_ingest and not to_index:
            print("  nothing waiting — every source file has markdown, every asset has a row")
            return 0

        def show(items, heading, follow_up):
            if not items:
                return
            print(f"  {len(items)} {heading}:\n")
            area = None
            for label, path in items:
                if label != area:
                    area, _ = label, print(f"  {label}/")
                print(f"      {path.relative_to(root / label)}")
            print(f"\n  → {follow_up}\n")

        show(to_ingest, "document(s) waiting to be INGESTED",
             "convert each, then update that bucket's canonical pair (eng-update-canonical).")
        show(to_index, "asset(s) of OURS waiting to be INDEXED",
             "eng-index-assets — what each proves, its date, whether it is in-window. "
             "An asset with no row is invisible to the bid.")
        return 0

    if not args.source:
        ap.error("give a document to convert, or --scan to list what is waiting")

    src = os.path.abspath(args.source)
    if not os.path.exists(src):
        print(f"ERROR: source not found: {src}", file=sys.stderr)
        return 2
    ext = os.path.splitext(src)[1].lower()
    fn = DISPATCH.get(ext)
    if not fn:
        print(f"ERROR: unsupported type '{ext}'. Supported: {', '.join(sorted(DISPATCH))}", file=sys.stderr)
        return 2

    out_path = os.path.abspath(args.out) if args.out else os.path.splitext(src)[0] + ".md"
    images_dir = os.path.abspath(args.images_dir) if args.images_dir else os.path.join(os.path.dirname(out_path), "images")
    os.makedirs(images_dir, exist_ok=True)

    body, err = fn(src, images_dir)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 3
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(body)
    print(f"Wrote {out_path}")
    print(f"md5(source) = {md5(src)}")
    print("Next: triage extracted images, OCR any [uncertain] ones inline, add the manifest "
          "row in _md/README.md, then run `eng-update-canonical`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
