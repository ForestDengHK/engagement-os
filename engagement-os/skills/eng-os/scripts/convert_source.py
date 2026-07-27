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

Supported: .pdf .pptx .ppsx .docx .xlsx .csv .png .jpg .jpeg .html .htm
Dependencies are imported lazily; a missing one degrades that format with a clear message
rather than crashing. Install as needed: pip install pymupdf python-pptx python-docx openpyxl
(PEP-668/Homebrew Python: add --user --break-system-packages, or use a venv.)

A sourced-from-the-web document has an origin URL that the file itself does not carry, and a
research claim has to cite something retrievable. Pass `--source-url` and it lands in the
provenance header next to the path and the md5.
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


# Set from --source-url. A document we downloaded has an origin the file does not record, and
# a research claim must cite something a reader can retrieve — so it belongs in the header,
# beside the path and the md5, for every format and not just HTML.
SOURCE_URL = None


def header(src, extra=""):
    origin = f"> **Origin URL:** {SOURCE_URL}  \n" if SOURCE_URL else ""
    return (
        f"# {os.path.basename(src)}\n\n"
        f"> **Source:** `{src}`  \n"
        f"{origin}"
        f"> **Converted:** {_dt.date.today().isoformat()}  \n"
        f"> **md5:** `{md5(src)}`  \n"
        f"{extra}\n---\n\n"
    )


MIN_IMG_BYTES = 6 * 1024        # below this is an icon, bullet, rule or spacer
MIN_IMG_PIXELS = 120            # narrowest side; logos and dividers fall under this


def img_prefix(src):
    """Namespace for one document's extracted images inside a shared pack images dir."""
    stem = os.path.splitext(os.path.basename(src))[0]
    return re.sub(r"[^A-Za-z0-9._-]+", "_", stem) + "__"


class ImageCollector:
    """Collects extracted images, dropping the ones that are decorative by construction.

    Two heuristics do almost all the work, and both are decidable from the bytes:

    * **Repeats.** A raster that appears on more than one page/slide is template furniture —
      a logo, a footer mark, a divider. Content diagrams do not repeat. This is the strong one.
    * **Size.** Under a few KB, or narrower than ~120px, it is an icon or a rule.

    Everything dropped is counted and reported, so the pass stays auditable: the lossless rule
    is about not losing *information*, and a logo carries none. What survives is what a human
    would actually have to look at.

    Links are written relative to **the markdown file**, not to the images dir's parent. Those
    two coincide only when the images dir is exactly `<md_dir>/images`; every other layout the
    skill actually instructs (`_md/images/<topic>/`) produced links that resolved nowhere.

    Names are namespaced by source document. The per-unit name a converter generates
    (`p6_img1.png`) is unique only *within* one document, but a reference pack points every
    document at ONE shared images dir — so the eleventh document's page 6 quietly overwrote the
    first document's page 6. The markdown still rendered, still had a plausible caption stub, and
    now showed a different report's figure under our citation. Found on the Deloitte research
    E2E: 27 names claimed by 2-5 documents each. Prefixing with the source stem makes the
    filename mean what the citation says it means.
    """

    def __init__(self, images_dir, link_base=None, prefix=""):
        self.dir = images_dir
        self.link_base = link_base or os.path.dirname(images_dir.rstrip("/"))
        self.prefix = prefix
        self.kept = []                  # (relpath, unit) in emit order
        self._by_digest = {}            # digest -> [(path, rel, unit), ...]
        self._names = {}                # emitted filename -> relpath (for inline placement)
        self.dropped_small = 0

    def add(self, blob, unit, name):
        """Offer one image. Returns True if written to disk."""
        if len(blob) < MIN_IMG_BYTES:
            self.dropped_small += 1
            return False
        name = self.prefix + os.path.basename(name)
        digest = hashlib.md5(blob).hexdigest()
        path = os.path.join(self.dir, name)
        os.makedirs(self.dir, exist_ok=True)
        with open(path, "wb") as f:
            f.write(blob)
        rel = os.path.relpath(path, self.link_base)
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
                self._names[os.path.basename(rel)] = rel
        self.kept.sort(key=lambda t: t[1])
        return self.kept, dropped_repeat

    def link_for(self, name):
        """Relative link for a kept image by filename, or None if it was dropped.
        `finalise()` must have run — decorative-drop is only decidable across the whole doc.

        Callers hold the un-prefixed name they generated, while `_names` is keyed by the
        namespaced one, so try both rather than making every call site know about the prefix.
        """
        base = os.path.basename(name)
        return self._names.get(self.prefix + base) or self._names.get(base)


IMG_TOKEN = "<!--ENGOS-IMG:%s-->"
_IMG_TOKEN_RE = re.compile(r"[ \t]*<!--ENGOS-IMG:(.+?)-->[ \t]*")


def img_block(rel, alt=""):
    """A placed image plus the caption stub that keeps the placement honest.

    A figure with no caption is only half-ingested: the reader (and every downstream claim) has
    the pixels but not what the document said the pixels mean. The stub is deliberately visible
    and deliberately tagged — `eng_lint.py` fails on a surviving `[caption-needed]`, so an
    unexplained diagram cannot quietly reach an analysis the way it did on the real GNI pack.
    """
    label = alt.strip() or os.path.basename(rel)
    return (f"\n![{label}]({rel})\n\n"
            f"*Figure `{os.path.basename(rel)}` — `[caption-needed]`: say what this shows, in the "
            f"words of the surrounding clause; if it carries text, OCR it inline first.*\n")


def place_inline_images(md, coll):
    """Resolve the inline placement tokens the converters emitted.

    An image only means something where it sat in the document — a scoring table or an
    architecture diagram listed at the bottom of the file under "triage these" has lost the
    clause it belonged to. But whether an image survives the decorative filter is only decidable
    once the whole document has been read, so the converters emit a token in place and this
    resolves it afterwards: kept → a markdown image at its original position, dropped → gone.
    """
    def sub(m):
        rel = coll.link_for(m.group(1))
        return img_block(rel) if rel else ""
    return _IMG_TOKEN_RE.sub(sub, md)


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
    # Careful with the wording: the lint counts occurrences of the caption tag, so this preamble
    # must describe the stub without spelling it — boilerplate that names its own marker makes
    # every converted file permanently fail the rule it exists to serve.
    lines = ["\n---\n\n## Images extracted — triage these\n", note,
             "Each is also **placed inline** at the position it held in the source, under a "
             "caption stub. This index is the checklist: classify each `[decorative]` (delete "
             "the file, the inline block and this line) / `[content]` (keep + write the caption) "
             "/ `[uncertain]` (OCR inline, then retag `[ocr-done]`). Do not delete an "
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


MAX_HEADING_CHARS = 120     # above this it is a mis-styled paragraph, not a heading


def _plain_heading(title):
    """Strip the emphasis wrapper pandoc faithfully carries into a heading.

    A real Word heading arrives as `**4.5. DECLARATION...**` or `<u>5.2. COST EVALUATION</u>`
    because the style bolded it. Keeping the wrapper leaves `## Section 42: **SCOPE**` in the
    output and makes the clause detection read the `**` instead of the number.
    """
    t = title.strip()
    t = re.sub(r"^(?:(?:\*\*|__|<u>|\[)\s*)+", "", t, flags=re.I)
    t = re.sub(r"(?:\s*(?:\*\*|__|</u>|\]))+$", "", t, flags=re.I)
    return t.strip()


def number_headings(md, label="Section"):
    """Give every markdown heading a stable, citable anchor, keeping its level.

    The extraction tools return the document's real heading hierarchy; what they can't give is
    an anchor a downstream claim can cite. A buyer's native clause number is the strongest
    anchor because it survives pagination and matches what an evaluator sees: `## 2.1 Timetable`
    becomes `## §2.1 Timetable`. Only headings without a native number get the synthetic
    fallback (`## Section 12: Minimum Requirements`). The outline hierarchy is never flattened.

    Three things the first version got wrong, all visible on the real GNI RFT:
    * the synthetic counter counted the `§`-numbered headings too, so the fallback sequence
      arrived full of holes (`Section 50` → `§4.5` → `Section 53`) and read like data loss;
    * an empty styled paragraph became a bare `#` — a heading with no text and no anchor;
    * a whole paragraph styled as Heading 3 in Word became `### Section 21: • The Contracting
      Entity may withhold payments pursuant to...`, which is body text wearing an anchor. A
      heading longer than `MAX_HEADING_CHARS` is demoted back to a paragraph; the text is kept,
      only the false anchor goes.
    """
    out, anchors, synthetic = [], 0, 0
    native = re.compile(
        r"^(?:(?:section|clause)\s+)?"
        r"(?P<num>\d{1,3}(?:\.\d{1,3}){0,5})"
        r"(?:\s*[.):\-–—]\s*|\s+)(?P<title>.+)$",
        re.I)
    for line in md.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if not m:
            out.append(line)
            continue
        title = _plain_heading(m.group(2))
        if not title:
            continue                                 # empty styled paragraph — drop, don't anchor
        if len(title) > MAX_HEADING_CHARS:
            out.append(title)                        # mis-styled paragraph — keep text, drop anchor
            continue
        anchors += 1
        if title.startswith("§"):
            out.append(f"{m.group(1)} {title}")
            continue
        clause = native.match(title)
        if clause:
            out.append(f"{m.group(1)} §{clause.group('num')} {clause.group('title').strip()}")
        else:
            synthetic += 1
            out.append(f"{m.group(1)} {label} {synthetic}: {title}")
    return "\n".join(out), anchors


_TOC_NESTED = re.compile(r"\[([^\[\]]*?)\s*\[(\d+)\]\(#[^)]*\)\]\(#[^)]*\)")
_INTERNAL_LINK = re.compile(r"\[([^\[\]]*)\]\(#[^)]*\)")


def flatten_internal_links(md):
    """Turn Word's exported table of contents back into readable text.

    Pandoc renders a TOC field as a link whose own label contains another link —
    `[1. IMPORTANT INFORMATION [4](#important-information)](#important-information)`. That is
    not valid nesting in GFM, so it renders as literal brackets, and a hundred lines of it is
    the first thing anyone reading the converted RFT sees. The anchors are worthless anyway:
    `number_headings` rewrites the heading ids they point at. Keep the text and the page number,
    drop the link machinery. External links are untouched.
    """
    md = _TOC_NESTED.sub(lambda m: f"{m.group(1)} — p.{m.group(2)}", md)
    return _INTERNAL_LINK.sub(lambda m: m.group(1), md)


def _pptx_shapes(container):
    """Yield shapes depth-first: a grouped diagram keeps its labels in child shapes, and
    `slide.shapes` only yields the top level — those labels would be lost silently."""
    for sh in container:
        if getattr(sh, "shape_type", None) == 6:      # GROUP
            yield from _pptx_shapes(sh.shapes)
        else:
            yield sh


def convert_pdf(src, images_dir, link_base=None):
    try:
        import fitz  # pymupdf
    except ImportError:
        return None, "pymupdf not installed — run: pip install pymupdf (PEP-668: add --user --break-system-packages)"
    doc = fitz.open(src)
    out = [header(src, f"> **Pages:** {doc.page_count}  ")]
    coll = ImageCollector(images_dir, link_base, img_prefix(src))
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
                name = f"p{i}_img{j}.png"
                if coll.add(pix.tobytes("png"), i, name):
                    out.append(IMG_TOKEN % name)     # resolved after the decorative filter runs
            except Exception:
                continue
    tail = img_section(coll)                         # runs finalise(); must precede placement
    return place_inline_images("\n".join(out), coll) + tail, None


def convert_pptx(src, images_dir, link_base=None):
    try:
        from pptx import Presentation
    except ImportError:
        return None, "python-pptx not installed — run: pip install python-pptx (PEP-668: add --user --break-system-packages)"
    prs = Presentation(src)
    coll = ImageCollector(images_dir, link_base, img_prefix(src))

    # markitdown owns the text: it reaches shape types python-pptx makes you hunt for and
    # carries each picture's embedded accessibility description, which is often the only
    # written account of a diagram. python-pptx still does the image FILES — markitdown
    # names images but does not write them, and the pack needs them on disk for triage.
    if _tool("markitdown"):
        md = _run(["markitdown", src])
        if md:
            body = re.sub(r"<!--\s*Slide number:\s*(\d+)\s*-->", r"## Slide \1:", md)
            by_slide = {}
            for i, slide in enumerate(prs.slides, 1):
                for shape in _pptx_shapes(slide.shapes):
                    if getattr(shape, "shape_type", None) == 13:
                        try:
                            name = f"s{i}_{shape.shape_id}.{shape.image.ext}"
                            if coll.add(shape.image.blob, i, name):
                                by_slide.setdefault(i, []).append(name)
                        except Exception:
                            continue
            # markitdown names pictures but writes no files, so it emits no link either.
            # Park each slide's images at the end of that slide's block, not at the end of
            # the deck: a diagram three slides away from its narrative is a diagram nobody
            # can caption.
            if by_slide:
                parts = re.split(r"(?m)^(## Slide (\d+):)$", body)
                rebuilt = [parts[0]]
                for k in range(1, len(parts), 3):
                    chunk = parts[k + 2]
                    toks = "".join("\n" + IMG_TOKEN % n for n in by_slide.get(int(parts[k + 1]), []))
                    rebuilt.append(parts[k] + chunk.rstrip("\n") + toks + "\n")
                body = "".join(rebuilt)
            head = header(src, f"> **Slides:** {len(prs.slides)}  \n> **Extractor:** markitdown  ")
            tail = img_section(coll)
            return head + place_inline_images(body, coll) + tail, None

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
                    name = f"s{i}_{shape.shape_id}.{image.ext}"
                    if coll.add(image.blob, i, name):
                        out.append(IMG_TOKEN % name)
                except Exception:
                    continue
        try:
            if slide.has_notes_slide:
                notes = slide.notes_slide.notes_text_frame.text.strip()
                if notes:
                    out.append(f"**Speaker notes:**\n\n{notes}\n")
        except Exception:
            pass
    tail = img_section(coll)
    return place_inline_images("\n".join(out), coll) + tail, None


def convert_docx(src, images_dir, link_base=None):
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
            coll = ImageCollector(images_dir, link_base, img_prefix(src))
            for root, _dirs, files in os.walk(tmp):
                for fn in sorted(files):
                    src_img = os.path.join(root, fn)
                    try:
                        with open(src_img, "rb") as fh:
                            coll.add(fh.read(), fn, fn)
                    except OSError:
                        continue
            shutil.rmtree(tmp, ignore_errors=True)
            tail = img_section(coll)                 # finalise() before any link_for() call

            # Pandoc points every image at the temp dir we just deleted. Repoint the survivors
            # at the pack's images dir and drop the links to images the filter removed, so the
            # markdown carries no dead references.
            #
            # BOTH syntaxes, not just markdown. Pandoc emits raw HTML `<img src=... style=.../>`
            # whenever the Word image carries an explicit size — which is nearly always. The
            # first version only rewrote `![](…)`, so on the real GNI tender pack every single
            # figure in every converted docx pointed into a temp directory that no longer
            # existed. The failure was invisible: the text conversion "succeeded".
            def _fix_md(m):
                rel = coll.link_for(m.group(2))
                return img_block(rel, m.group(1)) if rel else ""

            def _fix_html(m):
                tag = m.group(0)
                srcm = re.search(r'src\s*=\s*["\']([^"\']+)["\']', tag)
                if not srcm:
                    return ""
                rel = coll.link_for(srcm.group(1))
                if not rel:
                    return ""
                altm = re.search(r'alt\s*=\s*["\']([^"\']*)["\']', tag)
                return img_block(rel, altm.group(1) if altm else "")

            md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _fix_md, md)
            md = re.sub(r"<img\b[^>]*/?>", _fix_html, md, flags=re.I)
            md = flatten_internal_links(md)
            body, n = number_headings(md, "Section")
            head = header(src, f"> **Sections:** {n}  \n> **Extractor:** pandoc  ")
            return head + body + tail, None

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


def convert_xlsx(src, images_dir, link_base=None):
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


def convert_csv(src, images_dir, link_base=None):
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


def convert_html(src, images_dir, link_base=None):
    """A saved web page — the research lane's most common source, and the one with no file format.

    `defuddle` owns the de-cluttering, the way pandoc owns document order. A page saved from a
    corporate site is 90% navigation, cookie wall, share widgets and script tags; pandoc converts
    all of it faithfully into noise, which is worse than losing it. Defuddle is the same tool the
    `defuddle` skill reads pages with, so this is reuse, not a second implementation. We add only
    the provenance header and the citable section numbering.

    Images are remote here, not embedded, so there is nothing to extract to disk. Absolute links
    survive because they still resolve; relative ones are dropped, because a page saved without
    its origin turns `/content/dam/x.png` into a reference that points nowhere — the same dead-link
    failure convert_docx fixes for embedded media.
    """
    if _tool("defuddle"):
        md = _run(["defuddle", "parse", src, "-m"])
        extractor = "defuddle (page furniture removed)"
    else:
        md, extractor = None, None
    if not md and _tool("pandoc"):
        md = _run(["pandoc", "-f", "html", "-t", "gfm", "--wrap=none", src])
        extractor = ("pandoc (fallback — navigation, cookie banners and share widgets are "
                     "converted along with the article; install defuddle for a clean read)")
    if not md:
        return None, ("no defuddle and no pandoc — install either: "
                      "npm i -g defuddle-cli | brew install pandoc")

    kept, dropped = [0], [0]

    def _keep_absolute(m):
        url = m.group(2).strip()
        if url.lower().startswith(("http://", "https://", "data:")):
            kept[0] += 1
            return m.group(0)
        dropped[0] += 1
        return ""

    md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _keep_absolute, md)

    # Unglue headings fused onto the previous paragraph. Web markup routinely closes a block
    # without a break, so the converter emits `...scales as your needs evolve.#### Zora AI for
    # Finance`. A heading that is not at line start is not a heading to any markdown parser, so
    # it silently skips the anchor numbering below — and a section with no anchor cannot be
    # cited, which is the whole point of ingesting it. Require a non-space before the hashes so
    # a legitimate mid-sentence `# ` is left alone.
    md = re.sub(r"([^\s])(#{1,6} )", r"\1\n\n\2", md)

    md = flatten_internal_links(md)
    body, n = number_headings(md, "Section")
    note = f"> **Images:** {kept[0]} remote link(s) kept, {dropped[0]} relative link(s) dropped  \n"
    return header(src, f"> **Sections:** {n}  \n{note}> **Extractor:** {extractor}  ") + body, None


def convert_image(src, images_dir, link_base=None):
    rel = os.path.relpath(src, link_base or os.path.dirname(images_dir)) if images_dir else src
    body = header(src) + (
        f"## Image\n\n`[uncertain]` ![{os.path.basename(src)}]({rel})\n\n"
        "_This is an image source — OCR it inline (agent + vision), then retag `[ocr-done]`._\n"
    )
    return body, None


DISPATCH = {
    ".pdf": convert_pdf, ".pptx": convert_pptx, ".ppsx": convert_pptx,
    ".docx": convert_docx, ".xlsx": convert_xlsx, ".csv": convert_csv,
    ".png": convert_image, ".jpg": convert_image, ".jpeg": convert_image,
    ".html": convert_html, ".htm": convert_html,
}


def scan(root):
    """What showed up in the tree that hasn't been dealt with yet.

    Asking the user to type a path for every arriving document is asking them to do what a
    directory listing can decide. Two kinds of "not dealt with", because the two kinds of
    material have different destinations:

      INGEST  — sourced material (given to us or found by us, plus the tender pack). Un-ingested
        when nothing named after it exists under the matching `_md/`. Needs no manifest.
      CONVERT — our OWN reusable assets under `01_pursuit/_shared/<kind>/` with no markdown
        under `_shared/_md/`. Assets get the SAME md-first treatment as sources: analysing
        binaries ad-hoc is what the pack forbids everywhere else ("analysing from the raw PDF
        is how citations get invented" — it is also how a €250k reference value gets misread
        on submission week).
      INDEX   — assets with no row in `firm_assets.md`. An asset with no row is invisible to
        the bid.

    Returns (to_ingest, to_index, to_convert), each [(area_label, path)].
    """
    to_ingest = []
    areas = [(p, p / "_md") for p in root.glob("_sources/*") if p.is_dir()]
    areas += [(p, p / "_md") for p in root.glob("01_pursuit/*/1_received") if p.is_dir()]
    for area, md_dir in areas:
        converted = {p.stem.lower() for p in md_dir.rglob("*.md") if p.name != "README.md"} \
            if md_dir.exists() else set()
        for src in sorted(area.rglob("*")):
            if not src.is_file() or src.suffix.lower() not in DISPATCH:
                continue
            if md_dir in src.parents:            # already inside _md/ — an extracted image
                continue
            if src.stem.lower() not in converted:
                to_ingest.append((str(area.relative_to(root)), src))

    to_index, to_convert = [], []
    for shared in root.glob("01_pursuit/_shared"):
        index_file = shared / "firm_assets.md"
        index_text = (index_file.read_text(encoding="utf-8", errors="replace")
                      if index_file.exists() else "")
        # A path mentioned under "Gaps — what we do NOT hold" is not handled evidence.
        # Keep the same boundary the lint uses when deciding which A-nnn ids are real assets.
        index_text = re.split(r"^#{1,3}\s+.*gap.*$", index_text,
                              flags=re.M | re.I)[0]
        # A basename substring is not an identity. On the real GNI asset tree,
        # `case_studies/others/Quals.pdf` disappeared because the index already contained
        # `case_studies/1_General_DataMod Quals.pdf`. Read exact, backticked paths instead.
        # The same mechanism lets the index mark editable companions and build helpers as
        # handled without pretending each one is a separate A-nnn evidence asset.
        indexed = set()
        primaries = set()
        for line in index_text.splitlines():
            tokens = re.findall(r"`([^`\n]+)`", line)
            # a row keyed by an A-nnn id is an Index row; its FIRST backticked path is the
            # conversion target — anything after it is a companion (one logical asset = one
            # conversion)
            is_row = bool(re.match(r"\s*\|?\s*A-\d{3}\b", line))
            for j, token in enumerate(tokens):
                rel = token.strip().replace("\\", "/")
                prefix = "01_pursuit/_shared/"
                if rel.startswith(prefix):
                    rel = rel[len(prefix):]
                if rel and not rel.startswith(("/", "../")) and "<" not in rel:
                    rel = pathlib.PurePosixPath(rel).as_posix()
                    indexed.add(rel)
                    if is_row and j == 0:
                        primaries.add(rel)
        # Walk ALL of _shared/, not a whitelist of kinds. The scaffold plants six, and the
        # folder's own README tells the user to add a new one rather than force a bad fit —
        # so a whitelist makes exactly the assets someone thought about hardest invisible.
        md_dir = shared / "_md"
        converted = {p.stem.lower() for p in md_dir.rglob("*.md")
                     if p.name not in ("README.md",)} if md_dir.exists() else set()
        for asset in sorted(shared.rglob("*")):
            if not asset.is_file() or asset.name.startswith("."):
                continue
            if asset.parent.name == "_md" or (shared / "_md") in asset.parents:
                continue                          # conversions, not assets
            if asset.name in ("README.md", "firm_assets.md"):
                continue
            # any file type — a rate card or a CV is an asset whether or not we can convert it
            rel = asset.relative_to(shared).as_posix()
            if rel not in indexed:
                where = asset.parent.relative_to(root)
                to_index.append((str(where), asset))
            if asset.suffix.lower() in DISPATCH and asset.stem.lower() not in converted:
                # one logical asset = one conversion: the row's FIRST path (its primary) or a
                # file nothing mentions (a new arrival). Companions and §1b helpers named
                # elsewhere in the index need no md of their own.
                if rel in primaries or rel not in indexed:
                    where = asset.parent.relative_to(root)
                    to_convert.append((str(where), asset))
    return to_ingest, to_index, to_convert


def update_manifest(out_path, src):
    """Upsert this conversion's provenance row in the pack's README.md manifest.

    Only fires when the output lands in a `_md/` pack directory — anywhere else there is no
    manifest convention to maintain. eng_lint's manifest-complete rule errors on a converted
    MD with no row, so if the converter doesn't write the row, every conversion lands the
    user in a lint error they can only clear by hand. Found on the real GNI tender pack:
    four documents converted, no manifest anywhere, and the error had no automated path out.

    Row format matches what rule_manifest_complete greps for: the .md name in backticks.
    """
    pack = pathlib.Path(out_path).parent
    if pack.name != "_md":
        return
    readme = pack / "README.md"
    row = (f"- `{os.path.basename(out_path)}` — converted from "
           f"`{os.path.basename(src)}` ({_dt.date.today().isoformat()})")
    if not readme.exists():
        readme.write_text(
            "# Conversion manifest\n\n"
            "One row per converted document: which source file it came from and when. "
            "Written by convert_source.py on each conversion; keep rows in sync on renames.\n\n"
            + row + "\n", encoding="utf-8")
        return
    text = readme.read_text(encoding="utf-8", errors="replace")
    name = os.path.basename(out_path)
    if f"`{name}`" in text:                      # re-conversion: refresh the row, don't duplicate
        text = re.sub(rf"^- `{re.escape(name)}`.*$", row, text, flags=re.M)
    else:
        text = text.rstrip("\n") + "\n" + row + "\n"
    readme.write_text(text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", nargs="?",
                    help="the document to convert. Omit it with --scan to find what is waiting.")
    ap.add_argument("--scan", metavar="ROOT", nargs="?", const=".",
                    help="list source files in the engagement tree with no markdown yet, "
                         "and exit. Answers 'what arrived that I haven't ingested?'")
    ap.add_argument("--out", help="output .md path (default: source with .md next to it)")
    ap.add_argument("--images-dir", help="dir for extracted images (default: <out_dir>/images)")
    ap.add_argument("--source-url", help="the URL this document was downloaded from — recorded "
                                         "in the provenance header so a claim can cite something "
                                         "retrievable, not just a local path")
    args = ap.parse_args()

    global SOURCE_URL
    SOURCE_URL = args.source_url

    if args.scan is not None:
        root = pathlib.Path(args.scan).resolve()
        to_ingest, to_index, to_convert = scan(root)
        if not to_ingest and not to_index and not to_convert:
            print("  nothing waiting — every source file has markdown, every asset has a row "
                  "and a conversion")
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
        show(to_convert, "asset(s) of OURS waiting to be CONVERTED to `_shared/_md/`",
             "eng-index-assets step 0 converts before indexing — the md layer is what analysis "
             "and page-level citation read; the binary is the evidence, not the working text.")
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

    body, err = fn(src, images_dir, os.path.dirname(out_path))
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 3
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(body)
    update_manifest(out_path, src)
    print(f"Wrote {out_path}")
    print(f"md5(source) = {md5(src)}")
    print("Next: triage extracted images, OCR any [uncertain] ones inline "
          "(the manifest row was written), then run `eng-update-canonical`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
