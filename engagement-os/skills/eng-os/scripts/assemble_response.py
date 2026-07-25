#!/usr/bin/env python3
"""Assemble per-section bid markdown into the buyer's required document.

The sections are written to be *checkable* — each carries a scoring note, a
traceability line and a review log. None of that ships. Doing the strip by hand
each time is how internal scaffolding reaches an evaluator, so it lives here.

Conversion itself is delegated (pandoc for docx, soffice for pdf); this script
owns only what is specific to the pack: order, strip, gate, and measure.

    python3 assemble_response.py --sections 3_drafting/sections \
        --out 3_drafting/_render --name volume2_technical --format both
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
FIG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
SHIPPABLE = {"reviewed-r2", "approved"}


def read_section(path):
    raw = open(path, encoding="utf-8").read()
    m = FM_RE.match(raw)
    meta, body = {}, raw
    if m:
        body = raw[m.end():]
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "\t", "#")):
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def strip_internal(body: str) -> str:
    """Remove everything that exists to make the draft checkable, not to be read."""
    lines = body.splitlines()
    out, i = [], 0
    while i < len(lines):
        line = lines[i]

        # scoring / reuse notes — blockquote blocks
        if line.lstrip().startswith(">"):
            while i < len(lines) and (lines[i].lstrip().startswith(">") or not lines[i].strip()):
                if not lines[i].strip() and i + 1 < len(lines) and not lines[i + 1].lstrip().startswith(">"):
                    break
                i += 1
            continue

        # review log — heading through end of that section
        if re.match(r"^##\s+Review log\b", line, re.I):
            i += 1
            while i < len(lines) and not re.match(r"^#{1,2}\s+", lines[i]):
                i += 1
            continue

        # traceability paragraph, and the rule that introduces it
        if line.strip().startswith("**Traceability.**"):
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

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def check_figures(body, section_dir, path):
    """A missing image degrades to alt text in pandoc — the document builds and the
    figure is simply gone. Fail loudly instead."""
    missing = []
    for ref in FIG_RE.findall(body):
        if ref.startswith(("http://", "https://")):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(section_dir, ref))):
            missing.append(ref)
    return [(path, m) for m in missing]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sections", required=True, help="directory of section .md files")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--name", default="volume", help="output basename")
    ap.add_argument("--order", help="comma-separated filenames in the buyer's order "
                                    "(default: filename sort)")
    ap.add_argument("--format", choices=["md", "docx", "pdf", "both", "pptx"], default="both",
                    help="pptx is a read-through artefact, not a client deck — see the warning "
                         "it prints")
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--size", default="10pt")
    ap.add_argument("--allow-unreviewed", action="store_true",
                    help="assemble sections that have not reached R2")
    args = ap.parse_args()

    sec_dir = os.path.abspath(args.sections)
    out_dir = os.path.abspath(args.out)
    os.makedirs(out_dir, exist_ok=True)

    files = ([os.path.join(sec_dir, f.strip()) for f in args.order.split(",")]
             if args.order else
             sorted(os.path.join(sec_dir, f) for f in os.listdir(sec_dir) if f.endswith(".md")))
    if not files:
        print("no section files found", file=sys.stderr)
        return 1

    parts, rows, missing, unreviewed, unresolved = [], [], [], [], []
    for path in files:
        meta, body = read_section(path)
        missing += check_figures(body, sec_dir, os.path.basename(path))
        status = meta.get("status", "draft")
        if status not in SHIPPABLE:
            unreviewed.append((os.path.basename(path), status))
        clean = strip_internal(body)
        # A VERIFY marker is an open question wearing the clothes of an answer. It is
        # body prose, so stripping it would ship the unsupported claim silently.
        n = clean.count("[⚠VERIFY]")
        if n:
            unresolved.append((os.path.basename(path), n))
        parts.append(clean)
        rows.append((meta.get("section") or os.path.basename(path),
                     status, len(clean.split()), meta.get("page_budget", "—")))

    if missing:
        print("FIGURE MISSING — refusing to assemble (pandoc would silently drop these):",
              file=sys.stderr)
        for f, m in missing:
            print(f"  {f}: {m}", file=sys.stderr)
        return 2

    if unreviewed and not args.allow_unreviewed:
        print("NOT REVIEWED — refusing to assemble (pass --allow-unreviewed to override):",
              file=sys.stderr)
        for f, s in unreviewed:
            print(f"  {f}: status={s}", file=sys.stderr)
        return 3

    if unresolved and not args.allow_unreviewed:
        print("UNRESOLVED [⚠VERIFY] IN BODY TEXT — refusing to assemble; these reach the "
              "evaluator as claims (pass --allow-unreviewed to override):", file=sys.stderr)
        for f, n in unresolved:
            print(f"  {f}: {n}", file=sys.stderr)
        return 5

    md_path = os.path.join(out_dir, args.name + ".md")
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("\n\n\\newpage\n\n".join(parts))

    print(f"{'section':44s} {'status':13s} {'words':>6s}  page budget")
    for name, status, words, budget in rows:
        print(f"{name[:44]:44s} {status:13s} {words:6d}  {budget}")
    print(f"\nwrote {md_path}")

    if args.format == "md":
        return 0

    if not shutil.which("pandoc"):
        print("pandoc not found — markdown written, conversion skipped", file=sys.stderr)
        return 4

    if args.format == "pptx":
        pptx_path = os.path.join(out_dir, args.name + ".pptx")
        subprocess.run(["pandoc", md_path, "-o", pptx_path,
                        f"--resource-path={sec_dir}:{os.path.dirname(sec_dir)}"], check=True)
        print(f"wrote {pptx_path}")
        print("\nNOTE: a response section is prose sized to a page budget, so it overflows onto "
              "untitled continuation slides and orphans figure captions. This output is for an "
              "internal read-through. A client-facing deck is a separate artefact — build its "
              "slides through the figure pipeline (HTML source -> editable pptx), not by "
              "reformatting the response.")
        return 0

    docx_path = os.path.join(out_dir, args.name + ".docx")
    subprocess.run(["pandoc", md_path, "-o", docx_path,
                    f"--resource-path={sec_dir}:{os.path.dirname(sec_dir)}",
                    "--metadata", f"mainfont={args.font}",
                    "--metadata", f"fontsize={args.size}"], check=True)
    print(f"wrote {docx_path}")

    if args.format in ("pdf", "both") and shutil.which("soffice"):
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf",
                            docx_path, "--outdir", td], check=True,
                           stdout=subprocess.DEVNULL)
            pdf_tmp = os.path.join(td, args.name + ".pdf")
            pdf_path = os.path.join(out_dir, args.name + ".pdf")
            shutil.copy(pdf_tmp, pdf_path)
        print(f"wrote {pdf_path}")
        if shutil.which("pdfinfo"):
            info = subprocess.run(["pdfinfo", pdf_path], capture_output=True, text=True).stdout
            pages = next((l.split(":")[1].strip() for l in info.splitlines()
                          if l.startswith("Pages")), "?")
            print(f"\nPAGES: {pages} — check this against the per-section budgets above. "
                  "A word estimate is an estimate; the limit is measured in delivered pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
