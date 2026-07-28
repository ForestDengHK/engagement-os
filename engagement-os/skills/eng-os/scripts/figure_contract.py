"""Machine-readable form of the figure block in a converted markdown pack.

The single source imported by convert_source.py (which WRITES the blocks),
triage_images.py (which REWRITES them) and eng_lint.py (which COUNTS them).
Change the shape in references/image-triage.md AND here in the same commit —
the doc explains, this module decides.

Before this existed the three scripts each carried their own copy of the same
literals and regexes. Nothing bound them: renaming the caption stub in the
converter left the triage tool matching a pattern that no longer occurred, so
`--apply` silently rewrote nothing and reported success. The class of bug is
the same one `section_contract.py` was extracted to stop.

The shape of one placed figure, as written by `convert_source.img_block`:

    ![<label>](<relpath>)

    *Figure `<name>` — `[caption-needed]`: say what this shows …*

and after `triage_images --apply` the stub is replaced by the real caption,
optionally followed by a collapsible block holding the figure's own text. Each
figure also has one line in the index at the end of the file:

    - `[uncertain]` ![<name>](<relpath>)

retagged `[content]` / `[ocr-done]` on triage, or deleted with the figure.
"""
import re

# ── the tags a figure can carry ───────────────────────────────────────────────
#: Written by the converter; every one must be resolved before the pack is used.
UNTRIAGED = "uncertain"
#: The verdicts `triage_images --apply` accepts. `decorative` deletes the figure,
#: so it never appears as a surviving tag.
VERDICTS = ("content", "decorative", "ocr-done")
#: Tags a figure may still carry after triage — what the accounting rule counts.
SURVIVING_TAGS = (UNTRIAGED, "content", "ocr-done")

#: The caption placeholder. Deliberately not spelled out in any boilerplate the
#: converter emits: the lint counts occurrences, so a preamble naming its own
#: marker would make every converted file permanently fail the rule.
CAPTION_STUB = "[caption-needed]"

# ── the accounting lines, in the order they appear under the images heading ────
EXTRACTED_LINE = "**Extracted:**"          # how many figures conversion produced
AUTODROP_LINE = "**Auto-dropped as decorative:**"   # what bytes alone ruled out
CONSOLIDATED_LINE = "**Consolidated into page snapshots:**"
LEDGER_LINE = "**Triage ledger.**"         # what the triage pass decided
#: Lines the triage pass preserves when it rewrites the images section — they
#: account for figures that never reached triage, which is half the audit.
PRESERVED_LINES = (EXTRACTED_LINE, AUTODROP_LINE, CONSOLIDATED_LINE)

# ── headings ──────────────────────────────────────────────────────────────────
HEADING_PENDING = "## Images extracted — triage these"
HEADING_DONE = "## Images — triaged"

# ── patterns ──────────────────────────────────────────────────────────────────
#: An index line awaiting triage; group 1 is the relative path.
INDEX_UNTRIAGED = re.compile(
    r"(?m)^- `\[" + UNTRIAGED + r"\]` !\[[^\]]*\]\(([^)]+)\)\s*$")
#: Any index line that survived triage — what reconciles against EXTRACTED_LINE.
INDEX_ANY = re.compile(r"(?m)^- `\[(" + "|".join(SURVIVING_TAGS) + r")\]`")
#: The extracted count the converter recorded; group 1 is the number.
EXTRACTED_COUNT = re.compile(r"(?m)^\*\*Extracted:\*\*\s*(\d+)\s*$")
#: A previously-written triage ledger, up to the surviving index or next section.
#: `triage_images` uses this on a re-triage so ledgers replace rather than stack.
LEDGER_BLOCK = re.compile(
    r"\n" + re.escape(LEDGER_LINE) + r".*?(?=\n- `\[|\n## |\Z)", re.S)
#: Placement token the converters emit inline, resolved once the whole document
#: has been read. May carry alt text after a `|`.
IMG_TOKEN = "<!--ENGOS-IMG:%s-->"
IMG_TOKEN_RE = re.compile(r"[ \t]*<!--ENGOS-IMG:(.+?)-->[ \t]*")


def placed_figure(rel, body):
    """One placed figure: the image, then what it shows."""
    import os
    return f"\n![{os.path.basename(rel)}]({rel})\n\n*Figure `{os.path.basename(rel)}` — {body}*\n"


def caption_stub_block(rel):
    """The figure as the converter leaves it — placed, and visibly unexplained.

    A figure with no caption is only half-ingested: the reader has the pixels but
    not what the document said they mean. The stub is deliberately visible and
    deliberately tagged, so an unexplained diagram cannot quietly reach an
    analysis the way it did on the real GNI pack.
    """
    return placed_figure(
        rel, f"`{CAPTION_STUB}`: say what this shows, in the words of the "
             "surrounding clause; if it carries text, OCR it inline first")


def stub_block_re(rel):
    """The placed figure plus its stub, including trailing blank lines.

    Trailing newlines are part of the match so deleting a decorative figure
    closes the hole it leaves rather than widening the gap between paragraphs.
    """
    return re.compile(
        r"\n!\[[^\]]*\]\(" + re.escape(rel) + r"\)\n\n"
        r"\*Figure `[^`]*` — `\[" + re.escape(CAPTION_STUB.strip("[]")) +
        r"\]`[^\n]*\n+")


def index_line_re(rel):
    """This figure's line in the triage index, awaiting a verdict."""
    return re.compile(
        r"(?m)^- `\[" + UNTRIAGED + r"\]` !\[[^\]]*\]\(" + re.escape(rel) + r"\)\n")
