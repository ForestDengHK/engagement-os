#!/usr/bin/env python3
"""Render a directory of markdown sections into the required output artefact.

Deliberately generic. It knows about *markdown sections that carry frontmatter and
reference figures* — nothing about bids, deliverables, or any phase. Anything
phase-specific arrives as a `--profile`, so the same engine serves a tender
response, a client report, or a plain set of notes.

It owns four things and nothing else:

    discover  what is in the directory, in what order, referencing which figures
    gate      refuse to build when the profile's preconditions are unmet
    strip     remove the scaffolding that exists to make a draft checkable
    route     hand off — pandoc for a document, a manifest for a deck

It does NOT design figures (`designing-figures` owns that), build slides
(`presentation-builder` owns that), or write content.

    # what is here, and would it build?
    python3 render_document.py --sections 3_drafting/sections --analyse

    # a document
    python3 render_document.py --sections 3_drafting/sections --out _render \\
        --name volume2 --to docx --profile bid

    # a manifest for presentation-builder to work from
    python3 render_document.py --sections 3_drafting/sections --out _render \\
        --name volume2 --to deck-manifest
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import section_contract as sc   # the single source for the section-file contract

FIG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
H1_RE = re.compile(r"^#\s+(.+)$", re.M)

# A profile is policy, not mechanism. Each entry says which section states are
# shippable, whether unresolved markers block the build, and whether the drafting
# scaffolding is stripped. Add a profile here; do not add an `if bid:` anywhere below.
#
# `strip` is per-profile because the scaffolding convention (a blockquote is a scoring
# note) belongs to the bid/deliverable section contract — applied to arbitrary
# markdown it silently deletes legitimate quotations, the same failure class as
# pandoc degrading a missing image to its alt text.
PROFILES = {
    "plain": {
        "shippable": None,             # no status gate
        "block_markers": [],
        "strip": False,                # render whatever is there, quotes included
        "why": "no gates — render whatever is there",
    },
    "bid": {
        "shippable": {"reviewed-r2", "approved"},
        "block_markers": ["[⚠VERIFY]"],
        "strip": True,
        "why": "a tender is scored once; an unfixed R1 finding or an open VERIFY "
               "reaches the evaluator as a claim",
    },
    "deliverable": {
        "shippable": {"reviewed", "approved", "issued"},
        "block_markers": ["[⚠VERIFY]"],
        "strip": True,
        "why": "a client deliverable carries our name; unvalidated facts do not ship in it",
    },
}


# ---------------------------------------------------------------- discover

def read_section(path):
    raw = open(path, encoding="utf-8").read()
    # Do not grow a render-local interpretation of the section contract. Lint and
    # render must parse the same file identically, including the template's inline
    # lifecycle comments.
    return sc.parse_frontmatter(raw)


def discover(sec_dir, order=None):
    files = ([os.path.join(sec_dir, f.strip()) for f in order.split(",")] if order else
             sorted(os.path.join(sec_dir, f) for f in os.listdir(sec_dir) if f.endswith(".md")))
    out = []
    for path in files:
        meta, body = read_section(path)
        figures = []
        for alt, ref in FIG_RE.findall(body):
            resolved = os.path.normpath(os.path.join(sec_dir, ref))
            remote = ref.startswith(("http://", "https://"))
            figures.append({
                "alt": alt, "ref": ref, "path": resolved,
                "exists": remote or os.path.exists(resolved),
                # the editable sibling matters: a reviewer who cannot edit a figure
                # sends the correction back as prose
                "editable": (not remote) and os.path.exists(os.path.splitext(resolved)[0] + ".pptx"),
                "source": (not remote) and os.path.exists(os.path.splitext(resolved)[0] + ".html"),
            })
        h1 = H1_RE.search(body)
        out.append({
            "file": os.path.basename(path), "path": path, "meta": meta, "body": body,
            "title": meta.get("section") or (h1.group(1).strip() if h1 else os.path.basename(path)),
            "status": meta.get("status", "draft"),
            "budget": meta.get("page_budget", meta.get("budget", "—")),
            "figures": figures,
        })
    return out


# ---------------------------------------------------------------- strip

def strip_internal(body: str, scaffolding: bool = True):
    """Remove everything that exists to make the draft checkable, not to be read.

    Returns (text, n_blockquote_lines_removed). With scaffolding=False nothing is
    removed — the plain profile renders what is there, because the blockquote =
    scoring-note convention only holds for sections written under the contract.
    """
    if not scaffolding:
        return body, 0
    lines = body.splitlines()
    out, i, n_quotes = [], 0, 0
    while i < len(lines):
        line = lines[i]

        if line.lstrip().startswith(">"):                      # scoring / reuse notes
            while i < len(lines) and (lines[i].lstrip().startswith(">") or not lines[i].strip()):
                if not lines[i].strip() and i + 1 < len(lines) \
                        and not lines[i + 1].lstrip().startswith(">"):
                    break
                if lines[i].lstrip().startswith(">"):
                    n_quotes += 1
                i += 1
            continue

        if re.match(r"^##\s+Review log\b", line, re.I):        # review log
            i += 1
            while i < len(lines) and not re.match(r"^#{1,2}\s+", lines[i]):
                i += 1
            continue

        if line.strip().startswith("**Traceability.**"):       # traceability + its rule
            while out and not out[-1].strip():
                out.pop()
            if out and re.match(r"^-{3,}\s*$", out[-1]):
                out.pop()
            i += 1
            while i < len(lines) and lines[i].strip():
                i += 1
            continue

        out.append(line)
        i += 1

    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n", n_quotes


# ---------------------------------------------------------------- gate

def gate(sections, profile, override):
    """Return (blocking, advisory). Blocking refuses the build."""
    pol = PROFILES[profile]
    blocking, advisory = [], []

    for s in sections:
        for f in s["figures"]:
            if not f["exists"]:
                # always blocking, in every profile: pandoc degrades a missing image to
                # its alt text, so the document builds and the figure is simply gone
                blocking.append(f"{s['file']}: figure not found — {f['ref']}")
            elif not f["editable"]:
                advisory.append(f"{s['file']}: {os.path.basename(f['ref'])} has no editable "
                                f".pptx sibling — a reviewer cannot correct it")

    if override:
        return blocking, advisory

    if pol["shippable"]:
        for s in sections:
            if s["status"] not in pol["shippable"]:
                blocking.append(f"{s['file']}: status={s['status']}, not in "
                                f"{sorted(pol['shippable'])}")
            if s["status"] not in sc.ALL_STATUSES:
                advisory.append(f"{s['file']}: status '{s['status']}' is not in the "
                                "section-contract vocabulary")
    for marker in pol["block_markers"]:
        for s in sections:
            n = strip_internal(s["body"], pol["strip"])[0].count(marker)
            if n:
                blocking.append(f"{s['file']}: {n}x unresolved {marker} in body text")
    return blocking, advisory


# ---------------------------------------------------------------- report

def report(sections, strip=True):
    print(f"{'section':42s} {'status':13s} {'words':>6s}  {'figs':>4s}  page budget")
    for s in sections:
        words = len(strip_internal(s["body"], strip)[0].split())
        figs = "".join("!" if not f["exists"] else ("e" if f["editable"] else "p")
                       for f in s["figures"]) or "—"
        print(f"{s['title'][:42]:42s} {s['status']:13s} {words:6d}  {figs:>4s}  {s['budget']}")
    print("  figures:  e = editable source present · p = png only · ! = MISSING")


# ---------------------------------------------------------------- typography

def reference_docx(font: str, size: str, paper: str, workdir: str) -> str:
    """Build a pandoc reference.docx with enforced typography and paper size.

    `--metadata mainfont=`/`fontsize=` only reach LaTeX/PDF output; the docx writer
    takes ALL typography from the reference document, so passing those flags for a
    docx target looked like enforcement and did nothing. Here we take pandoc's own
    default reference and rewrite the docDefaults in word/styles.xml plus the section
    page size in word/document.xml with stdlib zipfile — no python-docx dependency.
    OOXML font sizes are in half-points; page dimensions are in twentieths of a point.
    """
    half = str(int(float(size.rstrip("pt")) * 2))
    src = os.path.join(workdir, "reference-default.docx")
    subprocess.run(["pandoc", "-o", src, "--print-default-data-file", "reference.docx"],
                   check=True)

    import zipfile
    with zipfile.ZipFile(src) as z:
        members = {i.filename: z.read(i.filename) for i in z.infolist()}
    xml = members["word/styles.xml"].decode("utf-8")

    rfonts = (f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" '
              f'w:cs="{font}"/>')
    # docDefaults is the root of the style inheritance tree; overriding there covers
    # every style that doesn't set its own fonts (pandoc's defaults don't).
    m = re.search(r"<w:docDefaults>.*?</w:docDefaults>", xml, re.S)
    if not m:
        print("warning: reference.docx has no docDefaults — font not enforceable",
              file=sys.stderr)
    else:
        dd = m.group(0)
        dd = re.sub(r"<w:rFonts[^>]*/>", rfonts, dd, count=1)
        if f'<w:sz w:val="{half}"' not in dd:
            dd = re.sub(r'<w:sz w:val="\d+"\s*/>', f'<w:sz w:val="{half}"/>', dd, count=1)
            dd = re.sub(r'<w:szCs w:val="\d+"\s*/>', f'<w:szCs w:val="{half}"/>', dd, count=1)
        xml = xml[:m.start()] + dd + xml[m.end():]

    members["word/styles.xml"] = xml.encode("utf-8")

    paper_twips = {
        "a4": ("11906", "16838"),
        "letter": ("12240", "15840"),
    }
    width, height = paper_twips[paper]
    doc_xml = members["word/document.xml"].decode("utf-8")
    pg = f'<w:pgSz w:w="{width}" w:h="{height}"/>'
    if re.search(r"<w:pgSz\b[^>]*/>", doc_xml):
        doc_xml = re.sub(r"<w:pgSz\b[^>]*/>", pg, doc_xml)
    elif "</w:sectPr>" in doc_xml:
        doc_xml = doc_xml.replace("</w:sectPr>", f"  {pg}\n    </w:sectPr>", 1)
    else:
        print("warning: reference.docx has no sectPr — paper size not enforceable",
              file=sys.stderr)
    members["word/document.xml"] = doc_xml.encode("utf-8")

    out = os.path.join(workdir, "reference.docx")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    return out


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sections", required=True, help="directory of section .md files")
    ap.add_argument("--out", help="output directory (not needed for --analyse)")
    ap.add_argument("--name", default="document", help="output basename")
    ap.add_argument("--order", help="comma-separated filenames in the required order "
                                    "(default: filename sort)")
    ap.add_argument("--analyse", action="store_true",
                    help="report what is here and whether it would build; write nothing")
    ap.add_argument("--to", choices=["md", "docx", "pdf", "both", "deck-manifest"],
                    default="both")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="plain")
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--size", default="10pt")
    ap.add_argument("--paper", choices=["a4", "letter"], default="a4",
                    help="paper size for generated reference.docx (default: a4); ignored when "
                         "--reference-doc supplies the buyer's own template")
    ap.add_argument("--reference-doc",
                    help="a mandated .docx template — overrides --font/--size and is the "
                         "only typography mechanism that reaches the docx writer")
    ap.add_argument("--audience", help="who the deck is for (recorded in the deck manifest)")
    ap.add_argument("--decision", help="the decision the deck must produce (deck manifest)")
    ap.add_argument("--force", action="store_true",
                    help="build despite policy gates (never overrides a missing figure)")
    args = ap.parse_args()

    sec_dir = os.path.abspath(args.sections)
    if not os.path.isdir(sec_dir):
        print(f"not a directory: {sec_dir}", file=sys.stderr)
        return 1

    sections = discover(sec_dir, args.order)
    if not sections:
        print(f"no .md sections in {sec_dir}", file=sys.stderr)
        return 1

    pol = PROFILES[args.profile]
    report(sections, pol["strip"])
    blocking, advisory = gate(sections, args.profile, args.force)

    for a in advisory:
        print(f"  advisory: {a}")
    if blocking:
        print(f"\nWOULD NOT BUILD under profile '{args.profile}' "
              f"({PROFILES[args.profile]['why']}):", file=sys.stderr)
        for b in blocking:
            print(f"  {b}", file=sys.stderr)
        if not args.analyse:
            print("\n--force overrides policy gates; a missing figure is never overridable.",
                  file=sys.stderr)
            return 2

    if args.analyse:
        print(f"\nprofile '{args.profile}': "
              + ("WOULD BUILD" if not blocking else f"{len(blocking)} blocker(s)"))
        return 0

    if not args.out:
        print("--out is required unless --analyse", file=sys.stderr)
        return 1
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    # ---- route: deck. Hand off a manifest; do not build slides here.
    if args.to == "deck-manifest":
        manifest = {
            "source": sec_dir,
            "profile": args.profile,
            # The two things presentation-builder needs most, recorded in the file so
            # the handoff survives being re-run from the manifest alone.
            "audience": args.audience,
            "decision": args.decision,
            "sections": [{
                "title": s["title"], "file": s["file"], "status": s["status"],
                "body": strip_internal(s["body"], pol["strip"])[0],
                "figures": [{"png": f["path"],
                             "html_source": os.path.splitext(f["path"])[0] + ".html",
                             "editable_pptx": os.path.splitext(f["path"])[0] + ".pptx",
                             "caption": f["alt"]}
                            for f in s["figures"] if f["exists"]],
            } for s in sections],
        }
        mpath = os.path.join(out_dir, args.name + ".deck-manifest.json")
        with open(mpath, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
        print(f"\nwrote {mpath}")
        print("Hand this to the `presentation-builder` skill. It owns storyline, action titles, "
              "figure specs (via `designing-figures`) and the editable export. A deck is not a "
              "reformat of a document — prose sized to a page budget overflows onto untitled "
              "slides, so presentation-builder re-cuts the argument rather than paginating it.")
        return 0

    # ---- route: document.
    md_path = os.path.join(out_dir, args.name + ".md")
    parts, stripped_notes = [], []
    for s in sections:
        text, n_quotes = strip_internal(s["body"], pol["strip"])
        if n_quotes:
            # visible, not silent: under a strict profile a blockquote is BY CONTRACT a
            # scaffolding note, but a legitimate quotation would be deleted here too
            stripped_notes.append(f"{s['file']}: stripped {n_quotes} blockquote line(s) "
                                  "as drafting scaffolding")
        parts.append(text)
    for note in stripped_notes:
        print(f"  note: {note}", file=sys.stderr)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n\n\\newpage\n\n".join(parts))
    print(f"\nwrote {md_path}")
    if args.to == "md":
        return 0

    if not shutil.which("pandoc"):
        print("pandoc not found — markdown written, conversion skipped", file=sys.stderr)
        return 4

    with tempfile.TemporaryDirectory() as td:
        ref = args.reference_doc or reference_docx(args.font, args.size, args.paper, td)
        docx_path = os.path.join(out_dir, args.name + ".docx")
        subprocess.run(["pandoc", md_path, "-o", docx_path,
                        f"--resource-path={sec_dir}:{os.path.dirname(sec_dir)}",
                        "--reference-doc", ref], check=True)
    print(f"wrote {docx_path}")

    if args.to in ("pdf", "both") and shutil.which("soffice"):
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf",
                            docx_path, "--outdir", td], check=True, stdout=subprocess.DEVNULL)
            pdf_path = os.path.join(out_dir, args.name + ".pdf")
            shutil.copy(os.path.join(td, args.name + ".pdf"), pdf_path)
        print(f"wrote {pdf_path}")
        if shutil.which("pdfinfo"):
            info = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True).stdout
            pages = next((l.split(":")[1].strip() for l in info.splitlines()
                          if l.startswith("Pages")), "?")
            print(f"\nPAGES: {pages} — check against the budgets above. A word estimate is an "
                  "estimate; the limit is measured in pages of the delivered file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
