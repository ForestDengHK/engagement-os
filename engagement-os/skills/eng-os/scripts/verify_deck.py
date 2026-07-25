#!/usr/bin/env python3
"""verify_deck.py — the mechanical gate on an assembled .pptx, before it ships.

Assembling a deck is a solved problem and lives elsewhere (the `pptx` skill copies
slides; `presentation-builder` decides the storyline). What was NOT mechanised is the
check afterwards — so the two failures that actually shipped kept shipping:

  * a deck assembled as one full-bleed PNG per slide. It looks right on the machine
    that built it and is dead on arrival for a reviewer: nothing selectable, nothing
    correctable, no text to search. Client decks are native shapes, always.
  * a deck whose text is set in a font the recipient does not have and the package
    does not carry. It renders correctly for the author and overflows its boxes on
    the reviewer's Windows PowerPoint.

Neither is visible in a build log; both are visible in the package. Reads the OOXML
directly (stdlib zipfile — no python-pptx), so it runs anywhere the pack runs.

    python3 verify_deck.py deck.pptx [--expect N] [--review-copy] [--strict]

Exit 0 clean · 1 findings (errors, or warnings under --strict) · 2 unreadable.
"""
import argparse
import pathlib
import re
import sys
import zipfile

# Set by every mainstream Office install; safe to reference without embedding.
SAFE_FONTS = {
    "arial", "arial black", "calibri", "calibri light", "cambria", "candara",
    "comic sans ms", "consolas", "constantia", "corbel", "courier new", "georgia",
    "impact", "lucida sans unicode", "palatino linotype", "segoe ui",
    "segoe ui light", "segoe ui semibold", "symbol", "tahoma", "times new roman",
    "trebuchet ms", "verdana", "wingdings",
}

SLIDE_RE = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
TYPEFACE_RE = re.compile(r'typeface="([^"]+)"')
EMBEDDED_RE = re.compile(r"<p:embeddedFont>.*?typeface=\"([^\"]+)\"", re.S)
SLDSZ_RE = re.compile(r'<p:sldSz[^>]*cx="(\d+)"[^>]*cy="(\d+)"')
TEXT_RE = re.compile(r"<a:t>(.*?)</a:t>", re.S)
PIC_RE = re.compile(r"<p:pic>.*?</p:pic>", re.S)
SHAPE_RE = re.compile(r"<p:(sp|pic|graphicFrame|grpSp)[ >]")
EXT_RE = re.compile(r'<a:ext cx="(\d+)" cy="(\d+)"')
REL_TARGET_RE = re.compile(r'Target="([^"]+)"')


class Report:
    """Same shape as eng_lint's — one output convention across the pack."""

    def __init__(self, review_copy=False):
        self.errors, self.warns = [], []
        self.review_copy = review_copy

    def error(self, kind, where, msg):
        self.errors.append((kind, where, msg))

    def warn(self, kind, where, msg):
        self.warns.append((kind, where, msg))

    def policy(self, kind, where, msg):
        """An error on a client deck; a warning once --review-copy says it is not one."""
        (self.warn if self.review_copy else self.error)(kind, where, msg)


class Deck:
    """The parsed package: slides in presentation order, plus what the checks need."""

    def __init__(self, path):
        self.path = path
        with zipfile.ZipFile(path) as z:
            self.names = set(z.namelist())
            if "ppt/presentation.xml" not in self.names:
                raise ValueError("no ppt/presentation.xml — not a PowerPoint package")
            self.presentation = z.read("ppt/presentation.xml").decode("utf-8", "replace")
            self.slides = []            # [(name, xml)] in slideN numeric order
            for name in sorted((n for n in self.names if SLIDE_RE.match(n)),
                               key=lambda n: int(SLIDE_RE.match(n).group(1))):
                self.slides.append((name, z.read(name).decode("utf-8", "replace")))
            self.rels = {}              # slide name -> [rel targets]
            for name, _ in self.slides:
                rel = f"ppt/slides/_rels/{pathlib.PurePosixPath(name).name}.rels"
                if rel in self.names:
                    xml = z.read(rel).decode("utf-8", "replace")
                    self.rels[name] = REL_TARGET_RE.findall(xml)
        m = SLDSZ_RE.search(self.presentation)
        self.size = (int(m.group(1)), int(m.group(2))) if m else None
        self.embedded = {f.lower() for f in EMBEDDED_RE.findall(self.presentation)}
        self.flattened = set()      # filled by rule_flattened; one finding per slide


def label(name):
    return f"slide {SLIDE_RE.match(name).group(1)}"


def rule_slide_count(deck, r, expect):
    """Slide count matches what the assembly was supposed to produce."""
    if expect is None:
        return
    n = len(deck.slides)
    if n != expect:
        r.error("slide-count", deck.path.name,
                f"{n} slides, expected {expect} — the splice dropped or duplicated slides")


def rule_flattened(deck, r):
    """No slide is a picture of a slide — client decks stay natively editable."""
    if not deck.size:
        return
    sw, sh = deck.size
    for name, xml in deck.slides:
        if any(t.strip() for t in TEXT_RE.findall(xml)):
            continue                                   # has real text: not flattened
        for pic in PIC_RE.findall(xml):
            ext = EXT_RE.search(pic)
            if not ext:
                continue
            cx, cy = int(ext.group(1)), int(ext.group(2))
            if cx >= sw * 0.95 and cy >= sh * 0.95:
                r.policy("flattened-slide", f"{deck.path.name} {label(name)}",
                         "a full-bleed image with no text — nothing on this slide can be "
                         "selected, corrected or searched. Rebuild it from native shapes; "
                         "pass --review-copy only if this file is not the client artefact.")
                deck.flattened.add(name)
                break


def rule_editable_text(deck, r):
    """Every slide carries text a reviewer can edit."""
    for name, xml in deck.slides:
        if name in deck.flattened:
            continue                                   # already reported, one finding each
        if any(t.strip() for t in TEXT_RE.findall(xml)):
            continue
        if SHAPE_RE.search(xml):
            r.warn("no-text-on-slide", f"{deck.path.name} {label(name)}",
                   "no text runs — intentional only for a pure image or divider slide")
        else:
            r.warn("empty-slide", f"{deck.path.name} {label(name)}",
                   "no shapes at all — an artefact of the splice, or a placeholder left behind")


def rule_fonts(deck, r):
    """Fonts the deck uses are either universally installed or embedded in the package."""
    used = {}
    for name, xml in deck.slides:
        for face in set(TYPEFACE_RE.findall(xml)):     # per slide, not per run
            if face.startswith("+"):                   # +mn-lt etc: theme reference
                continue
            key = face.lower()
            if key in SAFE_FONTS or key in deck.embedded:
                continue
            used.setdefault(face, []).append(label(name))
    for face, slides in sorted(used.items()):
        where = (f"{len(slides)} slides ({', '.join(slides[:3])}, …)"
                 if len(slides) > 3 else ", ".join(slides))
        r.warn("font-not-embedded", f"{deck.path.name} [{face}]",
               f"used on {where} but neither a standard Office font nor embedded in the "
               "package — it will substitute and overflow its boxes on a machine without it. "
               "Embed it, install it on the recipient's machine, or restyle to a safe font.")


def rule_media(deck, r):
    """Every image a slide points at is actually in the package."""
    for name, _ in deck.slides:
        for target in deck.rels.get(name, []):
            if not target.startswith("../media/"):
                continue
            part = "ppt/" + target[len("../"):]
            if part not in deck.names:
                r.error("broken-media-ref", f"{deck.path.name} {label(name)}",
                        f"points at {target}, which is not in the package — PowerPoint "
                        "shows a placeholder box where the figure should be")


RULES = [rule_slide_count, rule_flattened, rule_editable_text, rule_fonts, rule_media]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", help="the assembled .pptx to check")
    ap.add_argument("--expect", type=int, help="slide count the assembly should have produced")
    ap.add_argument("--review-copy", action="store_true",
                    help="this file is an internal review artefact, not the client deck")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    path = pathlib.Path(args.deck)
    try:
        deck = Deck(path)
    except (zipfile.BadZipFile, ValueError, FileNotFoundError) as exc:
        print(f"  cannot read {path}: {exc}")
        return 2

    r = Report(review_copy=args.review_copy)
    rule_slide_count(deck, r, args.expect)
    for rule in RULES[1:]:
        rule(deck, r)

    for lvl, items in (("ERROR", r.errors), ("warn", r.warns)):
        for kind, where, msg in items:
            print(f"  {lvl:5} [{kind}] {where}\n         {msg}")

    print(f"\n{len(deck.slides)} slide(s) · {len(r.errors)} error(s) · {len(r.warns)} warning(s)")
    if not r.errors and not r.warns:
        print("✓ clean")
    return 1 if r.errors or (args.strict and r.warns) else 0


if __name__ == "__main__":
    sys.exit(main())
