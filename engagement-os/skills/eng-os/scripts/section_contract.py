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
    "depends_on":   "eng-propagate-change (additional load-bearing dependencies)",
    "status":       "lint + render gate",
}

FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)

REQ_ID_RE = re.compile(r"\bR-\d{3}\b")
ASSET_ID_RE = re.compile(r"\bA-\d{3}\b")
FIG_ID_RE = re.compile(r"\bF-\d{2}\b")
RESEARCH_ID_RE = re.compile(r"\bBR-\d{3}\b")
#: Figure FILES are named F-nn_<name>.ext — the id is followed by a word character,
#: so \b never matches there; use this against filenames, FIG_ID_RE against prose.
FIG_FILE_RE = re.compile(r"^(F-\d{2})_")

#: An unresolved fact. The explanatory form `[⚠VERIFY — what would close it]` is the one
#: the templates and every real pack actually write, so ANY matcher must accept it.
#: Matching the bare literal `[⚠VERIFY]` let eight markers through a render gate for real.
VERIFY_RE = re.compile(r"\[⚠VERIFY[^\]]*\]")

#: A review-log round label. Rounds ITERATE — R1 sends a section back, the author fixes it,
#: R1 runs again — and the contract says one row per pass, so the label carries a suffix
#: (`R1 (2nd pass)`, `R1b`, `R1 · re-check`). An exact `R\d+` match ignored those rows and
#: read a stale verdict as the latest one.
ROUND_LABEL_RE = re.compile(r"^R\d+\b")


def revise_status_for(status, delivery=False):
    """The send-back state for a section currently in `status` — the SAME round it passed.

    A `reviewed-r1` section pushed to `revise-r2` claims an R2 round that never ran; the
    mechanical invalidator must not invent review history it did not observe.
    `delivery` selects the plainer client-deliverable vocabulary, where `approved` sends
    back to `revise`. Returns None when the status is not one a gate may invalidate.
    """
    if delivery:
        return "revise" if status in ("reviewed", "approved", "issued") else None
    return {
        "reviewed-r1": "revise-r1",
        "reviewed-r2": "revise-r2",
        "approved": "revise-r2",            # bid: approval follows R2
        "reviewed": "revise",               # a delivery-vocabulary section under a bid path
        "issued": "revise",
    }.get(status)


def round_of(status):
    """The review round a status belongs to, for labelling an appended log row."""
    m = re.search(r"r(\d+)$", status or "")
    return f"R{m.group(1)}" if m else "R1"


def parse_frontmatter(text):
    """Return (meta, body). meta maps field → raw string value (lists unparsed)."""
    m = FM_RE.match(text)
    meta, body = {}, text
    if m:
        body = text[m.end():]
        for line in m.group(1).splitlines():
            if ":" in line and not line.startswith((" ", "\t", "#")):
                k, v = line.split(":", 1)
                # The planted template documents lifecycle values with an inline comment:
                # `status: draft  # draft → reviewed-r1 ...`. The comment is YAML
                # documentation, not part of the value. Strip only an unquoted `#` preceded
                # by whitespace so a quoted title such as "Workstream #2" survives.
                quoted, cut = None, None
                for i, ch in enumerate(v):
                    if ch in ("'", '"'):
                        if quoted == ch:
                            quoted = None
                        elif quoted is None:
                            quoted = ch
                    elif ch == "#" and quoted is None and i > 0 and v[i - 1].isspace():
                        cut = i
                        break
                if cut is not None:
                    v = v[:cut]
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
