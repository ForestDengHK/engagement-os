#!/usr/bin/env python3
"""
md2outlook.py — put a Markdown document on the macOS clipboard as Outlook-ready
rich text, so Cmd+V into an Outlook message keeps headings, bold, bullets and
(above all) real bordered tables.

Why this exists: Outlook does not render Markdown, and a plain `pbcopy` only
puts a text flavour on the clipboard. This writes the `«class HTML»` flavour,
which is what Outlook reads on paste.

Styling is deliberately email-safe: everything is inline CSS on the element
(Outlook's Windows client renders with the Word engine, which ignores <style>
blocks, flexbox, grid and floats), tables carry the border/cellpadding HTML
attributes as well as CSS, and fonts are restated on every cell because the
Word engine does not reliably inherit them into tables.

Usage:
    md2outlook.py FILE.md                  # whole file -> clipboard
    md2outlook.py FILE.md --section EMAIL  # only the <!-- EMAIL:START/END --> slice
    md2outlook.py FILE.md --out draft.html # also write the HTML
    md2outlook.py FILE.md --open           # also open it in the browser
    cat x.md | md2outlook.py -             # from stdin
"""
import argparse
import html
import os
import re
import subprocess
import sys
import tempfile

FONT = "Aptos, Calibri, 'Segoe UI', Arial, sans-serif"
SIZE = "11pt"
BODY = f"font-family:{FONT};font-size:{SIZE};color:#000000;"
BORDER = "1px solid #BFBFBF"
CELL = f"border:{BORDER};padding:5pt 8pt;vertical-align:top;{BODY}"

# tag -> inline style. Applied to the opening tag, merged with any existing style.
STYLES = {
    "h1": f"{BODY}font-size:16pt;font-weight:bold;margin:14pt 0 6pt 0;",
    "h2": f"{BODY}font-size:13pt;font-weight:bold;margin:12pt 0 5pt 0;",
    "h3": f"{BODY}font-size:11.5pt;font-weight:bold;margin:10pt 0 4pt 0;",
    "h4": f"{BODY}font-size:11pt;font-weight:bold;margin:10pt 0 4pt 0;",
    "p": f"{BODY}margin:0 0 9pt 0;",
    "ul": f"{BODY}margin:0 0 9pt 0;padding-left:22pt;",
    "ol": f"{BODY}margin:0 0 9pt 0;padding-left:22pt;",
    "li": f"{BODY}margin:0 0 3pt 0;",
    "table": f"border-collapse:collapse;border:{BORDER};margin:0 0 12pt 0;",
    "th": f"{CELL}background-color:#F2F2F2;font-weight:bold;text-align:left;",
    "td": CELL,
    "blockquote": f"{BODY}margin:0 0 9pt 0;padding:0 0 0 10pt;"
                  f"border-left:3px solid #D0D0D0;color:#404040;",
    "code": "font-family:Consolas,'Courier New',monospace;font-size:10pt;"
            "background-color:#F5F5F5;",
    "pre": "font-family:Consolas,'Courier New',monospace;font-size:9.5pt;"
           "background-color:#F5F5F5;border:1px solid #E0E0E0;"
           "padding:8pt;margin:0 0 12pt 0;white-space:pre;",
    "a": "color:#0563C1;",
    "hr": "border:0;border-top:1px solid #D0D0D0;margin:12pt 0;",
}


def slice_section(md: str, name: str) -> str:
    """Return the text between <!-- name:START --> and <!-- name:END -->."""
    m = re.search(
        r"<!--\s*%s:START\s*-->(.*?)<!--\s*%s:END\s*-->" % (name, name),
        md, re.S,
    )
    if not m:
        sys.exit(f"md2outlook: no <!-- {name}:START --> ... <!-- {name}:END --> "
                 f"markers found")
    return m.group(1)


def md_to_html(md: str) -> str:
    """Markdown -> HTML fragment via pandoc (GitHub-flavoured, so tables work)."""
    try:
        return subprocess.run(
            ["pandoc", "-f", "gfm", "-t", "html", "--wrap=none"],
            input=md, capture_output=True, text=True, check=True,
        ).stdout
    except FileNotFoundError:
        sys.exit("md2outlook: pandoc not found (brew install pandoc)")
    except subprocess.CalledProcessError as e:
        sys.exit(f"md2outlook: pandoc failed:\n{e.stderr}")


def inline_styles(frag: str) -> str:
    """Push an inline style onto every element Outlook cares about."""
    def apply(tag: str, style: str, extra_attrs: str = "") -> None:
        nonlocal frag

        def repl(m):
            attrs = m.group(1) or ""
            # Pandoc emits XHTML-style void tags (<hr />, <col ... />). Peel the
            # trailing slash off before appending, or we build "<hr / style=...>".
            selfclose = attrs.rstrip().endswith("/")
            if selfclose:
                attrs = attrs.rstrip()[:-1].rstrip()
                if attrs:
                    attrs = " " + attrs.lstrip()
            existing = re.search(r'style="([^"]*)"', attrs)
            if existing:
                merged = style + existing.group(1)
                attrs = attrs.replace(existing.group(0), f'style="{merged}"')
            else:
                attrs += f' style="{style}"'
            close = " />" if selfclose else ">"
            return f"<{tag}{extra_attrs}{attrs}{close}"

        frag = re.sub(r"<%s(\s[^>]*?)?\s*/?>" % tag, repl, frag, flags=re.I)

    # Word's engine honours these HTML attributes more reliably than the CSS.
    apply("table", STYLES["table"], ' border="1" cellspacing="0" cellpadding="0"')
    apply("th", STYLES["th"], ' bgcolor="#F2F2F2"')
    for tag in ("td", "h1", "h2", "h3", "h4", "p", "ul", "ol", "li",
                "blockquote", "code", "pre", "a", "hr"):
        apply(tag, STYLES[tag])
    return frag


def to_clipboard(html_doc: str, plain: str) -> None:
    """Write both the HTML and text flavours to the macOS pasteboard."""
    if sys.platform != "darwin":
        sys.exit("md2outlook: the clipboard path is macOS-only (it writes the\n"
                 "«class HTML» pasteboard flavour via osascript). On Windows or\n"
                 "Linux use --out FILE.html, open it in a browser, then Cmd/Ctrl+A,\n"
                 "Cmd/Ctrl+C and paste that into the message.")
    def esc(s: str) -> str:
        return (s.replace("\\", "\\\\").replace('"', '\\"')
                 .replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t"))

    hexed = html_doc.encode("utf-8").hex()
    script = (f'set the clipboard to {{text:"{esc(plain)}", '
              f'«class HTML»:«data HTML{hexed}»}}')
    with tempfile.NamedTemporaryFile("w", suffix=".applescript",
                                     delete=False, encoding="utf-8") as fh:
        fh.write(script)
        path = fh.name
    try:
        r = subprocess.run(["osascript", path], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"md2outlook: osascript failed:\n{r.stderr}")
    finally:
        os.unlink(path)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="Markdown file, or - for stdin")
    ap.add_argument("--section", help="only the named <!-- NAME:START/END --> slice")
    ap.add_argument("--out", help="also write the HTML here")
    ap.add_argument("--open", action="store_true", help="also open it in the browser")
    ap.add_argument("--no-clip", action="store_true", help="skip the clipboard")
    args = ap.parse_args()

    md = sys.stdin.read() if args.file == "-" else \
        open(args.file, encoding="utf-8").read()
    if args.section:
        md = slice_section(md, args.section)

    frag = inline_styles(md_to_html(md))
    doc = ('<html><head><meta charset="utf-8"></head>'
           f'<body style="{BODY}">{frag}</body></html>')

    if not args.no_clip:
        to_clipboard(doc, md)
    if args.out:
        open(args.out, "w", encoding="utf-8").write(doc)
    if args.open:
        path = args.out or os.path.join(tempfile.mkdtemp(), "outlook_draft.html")
        if not args.out:
            open(path, "w", encoding="utf-8").write(doc)
        subprocess.run(["open", path])

    where = []
    if not args.no_clip:
        where.append("clipboard (HTML flavour)")
    if args.out:
        where.append(args.out)
    print(f"md2outlook: {len(frag)} bytes of HTML -> {', '.join(where) or 'nowhere'}")
    if not args.no_clip:
        print("Now click into the Outlook message body and press Cmd+V.")


if __name__ == "__main__":
    main()
