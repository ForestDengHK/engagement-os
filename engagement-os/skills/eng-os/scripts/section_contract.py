"""Machine-readable form of references/section-contract.md.

The single source imported by eng_lint.py and render_document.py. Change the
contract in the reference doc AND here in the same commit — the doc explains,
this module decides.
"""
import re

# ── status vocabulary ─────────────────────────────────────────────────────────
# Happy path: draft → reviewed-r1 → reviewed-r2 → approved.
BID_STATUSES = {"draft", "reviewed-r1", "reviewed-r2", "revise-r1", "revise-r2",
                "blocked-r1", "blocked-r2", "approved"}
# Client-deliverable sections: draft → reviewed → approved → issued.
DELIVERABLE_STATUSES = {"draft", "reviewed", "revise", "blocked", "approved", "issued"}
ALL_STATUSES = BID_STATUSES | DELIVERABLE_STATUSES

#: A verdict in the review log pairs with exactly these statuses (lint checks the
#: pairing against the LATEST round, not just the two extremes).
VERDICT_STATUS = {
    "pass":    {"reviewed-r1", "reviewed-r2", "reviewed", "approved", "issued"},
    "revise":  {"revise-r1", "revise-r2", "revise"},
    "blocked": {"blocked-r1", "blocked-r2", "blocked"},
}

# ── frontmatter ───────────────────────────────────────────────────────────────
#: field → which mechanism consumes it (None = documentation only; the contract
#: doc says a field that looks enforced but isn't is worse than no field).
FIELDS = {
    "section":      "render (output title)",
    "rft_clause":   None,
    "marks":        None,
    "pass_mark":    None,
    "scoring":      None,
    "answers_reqs": "lint (ids must exist in the compliance matrix)",
    "page_budget":  "lint (per-file and shared-pool checks)",
    "figures":      "lint (ids must exist in figures/ and be referenced in the body)",
    "evidence":     "lint (ids must exist in firm_assets.md)",
    "status":       "lint + render gate",
}

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)

REQ_ID_RE = re.compile(r"\bR-\d{3}\b")
ASSET_ID_RE = re.compile(r"\bA-\d{3}\b")
FIG_ID_RE = re.compile(r"\bF-\d{2}\b")
#: Figure FILES are named F-nn_<name>.ext — the id is followed by a word character,
#: so \b never matches there; use this against filenames, FIG_ID_RE against prose.
FIG_FILE_RE = re.compile(r"^(F-\d{2})_")


def parse_frontmatter(text):
    """Return (meta, body). meta maps field → raw string value (lists unparsed)."""
    m = FM_RE.match(text)
    meta, body = {}, text
    if m:
        body = text[m.end():]
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "\t", "#")):
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def fm_list(meta, key, id_re):
    """Parse a frontmatter list field into clean ids, e.g. '[R-001, R-013]' → {'R-001','R-013'}.
    Placeholder values (<...>, R-0xx) yield nothing."""
    raw = meta.get(key, "")
    if "<" in raw:
        return set()
    return set(id_re.findall(raw))


def normalize_budget(s):
    """Pool key for shared page budgets: dashes, case and whitespace are decorative,
    the limit and its scope are not. Pooling on the raw string let two spellings of
    the same shared budget each pass per-file — the original silent-pass one level down."""
    s = s.lower().replace("‑", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()
