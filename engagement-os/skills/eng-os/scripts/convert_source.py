#!/usr/bin/env python3
"""Convert one source document to faithful, citable Markdown for the reference pack.

Deterministic extraction only: text + tables with per-page/slide anchors, plus image
extraction to a sibling images dir. IMAGE TRIAGE AND OCR ARE LEFT TO THE AGENT (a judgment +
vision task) — this script emits every extracted image tagged `[uncertain]` so the agent can
classify [decorative]/[content]/[uncertain] and OCR the uncertain ones inline. See the
`eng-ingest-source` skill.

Usage:
    python convert_source.py <source_path> [--out <md_path>] [--images-dir <dir>]

Supported: .pdf .pptx .ppsx .docx .xlsx .csv .png .jpg .jpeg
Dependencies are imported lazily; a missing one degrades that format with a clear message
rather than crashing. Install as needed: pip install pymupdf python-pptx python-docx openpyxl
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


def img_section(images):
    if not images:
        return ""
    lines = ["\n---\n\n## Images extracted — triage these\n",
             "Classify each `[decorative]` (delete) / `[content]` (keep + caption) / "
             "`[uncertain]` (OCR inline, then retag `[ocr-done]`). Do not delete an "
             "`[uncertain]` image before its text is captured.\n"]
    for im in images:
        lines.append(f"- `[uncertain]` ![{os.path.basename(im)}]({im})")
    return "\n".join(lines) + "\n"


def convert_pdf(src, images_dir):
    try:
        import fitz  # pymupdf
    except ImportError:
        return None, "pymupdf not installed — run: pip install pymupdf"
    doc = fitz.open(src)
    out = [header(src, f"> **Pages:** {doc.page_count}  ")]
    images = []
    for i, page in enumerate(doc, 1):
        out.append(f"## Page {i}:\n")
        text = page.get_text("text").strip()
        out.append(text + "\n" if text else "_(no extractable text — likely a diagram/image page; see extracted images)_\n")
        for j, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha >= 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                name = os.path.join(images_dir, f"p{i}_img{j}.png")
                pix.save(name)
                images.append(os.path.relpath(name, os.path.dirname(images_dir)))
            except Exception:
                continue
    return "\n".join(out) + img_section(images), None


def convert_pptx(src, images_dir):
    try:
        from pptx import Presentation
    except ImportError:
        return None, "python-pptx not installed — run: pip install python-pptx"
    prs = Presentation(src)
    out = [header(src, f"> **Slides:** {len(prs.slides)}  ")]
    images = []
    for i, slide in enumerate(prs.slides, 1):
        out.append(f"## Slide {i}:\n")
        for shape in slide.shapes:
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
                    name = os.path.join(images_dir, f"s{i}_{shape.shape_id}.{image.ext}")
                    with open(name, "wb") as f:
                        f.write(image.blob)
                    images.append(os.path.relpath(name, os.path.dirname(images_dir)))
                except Exception:
                    continue
    return "\n".join(out) + img_section(images), None


def convert_docx(src, images_dir):
    try:
        import docx  # python-docx
    except ImportError:
        return None, "python-docx not installed — run: pip install python-docx (or use the docx skill)"
    d = docx.Document(src)
    out = [header(src)]
    for para in d.paragraphs:
        if para.text.strip():
            style = (para.style.name or "").lower()
            prefix = "## " if "heading" in style else ""
            out.append(prefix + para.text.strip() + "\n")
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
        return None, "openpyxl not installed — run: pip install openpyxl (or use the xlsx skill)"
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
