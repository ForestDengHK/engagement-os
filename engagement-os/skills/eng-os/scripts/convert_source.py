#!/usr/bin/env python3
"""Convert one source document to faithful, citable Markdown for the reference pack.

Deterministic extraction only: text + tables with per-page/slide anchors, plus image
extraction to a sibling images dir.

Images that are decorative *by construction* are dropped here rather than pushed onto the agent:
a raster repeated across pages/slides is template furniture (logo, footer mark, divider) and one
under a few KB is an icon or rule. Both are counted and reported in the output, so the pass stays
auditable. Everything that survives is tagged `[uncertain]` for the agent to classify
[decorative]/[content] and OCR — that part is a judgment + vision task. See `eng-ingest-source`.

NOT a replacement for the `pptx` / `docx` / `pdf` / `xlsx` skills. This is bulk, deterministic,
zero-token extraction for ingesting many documents. Reach for the matching skill when a single
document matters more than throughput — tracked changes, comments, SmartArt, charts with data
labels, complex merged tables, or a scanned PDF needing real OCR.

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
    out = [header(src, f"> **Slides:** {len(prs.slides)}  ")]
    coll = ImageCollector(images_dir)
    for i, slide in enumerate(prs.slides, 1):
        out.append(f"## Slide {i}:\n")
        # Walk groups recursively: a grouped diagram keeps its labels in child shapes, and
        # `slide.shapes` only yields the top level — those labels would be lost silently.
        def shapes_of(container):
            for sh in container:
                if getattr(sh, "shape_type", None) == 6:      # GROUP
                    yield from shapes_of(sh.shapes)
                else:
                    yield sh
        for shape in shapes_of(slide.shapes):
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
    try:
        import docx  # python-docx
    except ImportError:
        return None, "python-docx not installed — run: pip install python-docx (or use the docx skill; PEP-668: add --user --break-system-packages)"
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

    out = [header(src, f"> **Sections:** {n}  ")]
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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source")
    ap.add_argument("--out", help="output .md path (default: source with .md next to it)")
    ap.add_argument("--images-dir", help="dir for extracted images (default: <out_dir>/images)")
    args = ap.parse_args()

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
