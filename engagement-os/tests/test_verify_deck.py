#!/usr/bin/env python3
"""Fixture tests for verify_deck.py — each check gets a passing and a failing deck.

The fixtures are synthesised OOXML packages built with stdlib zipfile, not real
PowerPoint files: verify_deck reads the package directly, so the tests carry no
python-pptx dependency and run wherever the pack runs.

Run after ANY edit to verify_deck.py.
"""
import pathlib
import re
import subprocess
import sys
import tempfile
import zipfile

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
VERIFY = PLUGIN / "skills/eng-os/scripts/verify_deck.py"

KIND_RE = re.compile(r"^\s*(ERROR|warn)\s+\[([\w-]+)\]")

SW, SH = 12192000, 6858000                      # 16:9 at 13.333in × 7.5in, in EMU


def presentation(embedded=()):
    fonts = "".join(f'<p:embeddedFont><p:font typeface="{f}"/></p:embeddedFont>'
                    for f in embedded)
    lst = f"<p:embeddedFontLst>{fonts}</p:embeddedFontLst>" if fonts else ""
    return ('<p:presentation xmlns:p="p" xmlns:a="a">'
            f'<p:sldIdLst/><p:sldSz cx="{SW}" cy="{SH}"/>{lst}</p:presentation>')


def slide(body):
    return ('<p:sld xmlns:p="p" xmlns:a="a"><p:cSld><p:spTree>'
            f'{body}</p:spTree></p:cSld></p:sld>')


def textbox(text, font="Arial"):
    return ('<p:sp><p:txBody><a:p><a:r>'
            f'<a:rPr><a:latin typeface="{font}"/></a:rPr><a:t>{text}</a:t>'
            '</a:r></a:p></p:txBody></p:sp>')


def picture(cx=SW, cy=SH):
    return ('<p:pic><p:blipFill><a:blip r:embed="rId1"/></p:blipFill>'
            f'<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/>'
            '</a:xfrm></p:spPr></p:pic>')


NATIVE = slide(textbox("The warehouse refresh is all-or-nothing"))
FLAT = slide(picture())
PIC_WITH_TEXT = slide(picture() + textbox("Figure 3 — the target shape"))
SMALL_PIC = slide(picture(cx=SW // 4, cy=SH // 4))
EMPTY = slide("")


def build(parts):
    """parts: {archive path: text}. Returns the written .pptx path."""
    out = pathlib.Path(tempfile.mkdtemp(prefix="engos-deck-")) / "deck.pptx"
    with zipfile.ZipFile(out, "w") as z:
        for name, content in parts.items():
            z.writestr(name, content)
    return out


def deck(slides, embedded=(), rels=None, media=()):
    parts = {"ppt/presentation.xml": presentation(embedded)}
    for i, xml in enumerate(slides, start=1):
        parts[f"ppt/slides/slide{i}.xml"] = xml
    for i, target in (rels or {}).items():
        parts[f"ppt/slides/_rels/slide{i}.xml.rels"] = (
            '<Relationships xmlns="r">'
            f'<Relationship Id="rId1" Target="{target}"/></Relationships>')
    for name in media:
        parts[f"ppt/media/{name}"] = "PNGDATA"
    return build(parts)


# (name, deck factory, extra argv, expected ERROR kinds, expected warn kinds,
#  kinds that must NOT fire)
CASES = [
    ("clean native deck",
     lambda: deck([NATIVE, NATIVE]), [], set(), set(),
     {"flattened-slide", "font-not-embedded", "empty-slide", "no-text-on-slide"}),

    ("full-bleed image slide is flattened",
     lambda: deck([NATIVE, FLAT]), [], {"flattened-slide"}, set(),
     {"no-text-on-slide"}),                     # one finding per slide, not two

    ("--review-copy downgrades flattening to a warning",
     lambda: deck([FLAT]), ["--review-copy"], set(), {"flattened-slide"}, set()),

    ("image WITH text is not flattened",
     lambda: deck([PIC_WITH_TEXT]), [], set(), set(),
     {"flattened-slide", "no-text-on-slide"}),

    ("a small picture and no text is not flattening",
     lambda: deck([SMALL_PIC]), [], set(), {"no-text-on-slide"}, {"flattened-slide"}),

    ("slide with no shapes at all",
     lambda: deck([NATIVE, EMPTY]), [], set(), {"empty-slide"}, {"no-text-on-slide"}),

    ("--expect mismatch fails the splice",
     lambda: deck([NATIVE, NATIVE]), ["--expect", "3"], {"slide-count"}, set(), set()),

    ("--expect match passes",
     lambda: deck([NATIVE, NATIVE]), ["--expect", "2"], set(), set(), {"slide-count"}),

    ("non-standard font neither installed nor embedded",
     lambda: deck([slide(textbox("Target shape", font="Open Sans"))]), [],
     set(), {"font-not-embedded"}, set()),

    ("the same font, embedded in the package",
     lambda: deck([slide(textbox("Target shape", font="Open Sans"))],
                  embedded=("Open Sans",)), [], set(), set(), {"font-not-embedded"}),

    ("a theme font reference is not a font",
     lambda: deck([slide(textbox("Target shape", font="+mn-lt"))]), [],
     set(), set(), {"font-not-embedded"}),

    ("figure relationship pointing outside the package",
     lambda: deck([NATIVE], rels={1: "../media/image1.png"}), [],
     {"broken-media-ref"}, set(), set()),

    ("figure relationship whose media IS in the package",
     lambda: deck([NATIVE], rels={1: "../media/image1.png"}, media=("image1.png",)),
     [], set(), set(), {"broken-media-ref"}),
]


def run(path, argv):
    proc = subprocess.run([sys.executable, str(VERIFY), str(path), *argv],
                          capture_output=True, text=True)
    errors, warns = set(), set()
    for line in proc.stdout.splitlines():
        m = KIND_RE.match(line)
        if m:
            (errors if m.group(1) == "ERROR" else warns).add(m.group(2))
    return errors, warns, proc.stdout, proc.returncode


def main():
    fails = []
    for name, factory, argv, want_err, want_warn, want_absent in CASES:
        errors, warns, out, _ = run(factory(), argv)
        ok = (errors == want_err and want_warn <= warns
              and not ((errors | warns) & want_absent))
        print(f"  {'✓' if ok else '✗'} {name}")
        if not ok:
            fails.append(name)
            print(f"      errors: got {sorted(errors)} want {sorted(want_err)}")
            print(f"      warns : got {sorted(warns)} want ⊇ {sorted(want_warn)}"
                  + (f" absent {sorted(want_absent)}" if want_absent else ""))

    # A file that is not a package must fail loudly, not report a clean deck.
    junk = pathlib.Path(tempfile.mkdtemp(prefix="engos-deck-")) / "not-a-deck.pptx"
    junk.write_text("this is not a zip")
    _, _, out, code = run(junk, [])
    ok = code == 2 and "cannot read" in out
    print(f"  {'✓' if ok else '✗'} an unreadable file exits 2, never 'clean'")
    if not ok:
        fails.append("unreadable file")

    total = len(CASES) + 1
    print(f"\n{total - len(fails)}/{total} cases pass")
    if fails:
        print(f"✗ FAILING: {fails}")
        return 1
    print("✓ all deck fixture cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
