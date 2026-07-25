#!/usr/bin/env python3
"""Fixture tests for eng_lint.py — every rule gets a clean tree and violated trees.

History: the pack used to claim "each rule tested both ways", but the tests were
ad-hoc mutations of a live testbed and were never persisted — a review found the
claim unverifiable from the repo. This file IS the persistence. A case is:

    (name, mutation applied to a fresh copy of the clean tree,
     exact expected ERROR kinds, expected WARN kinds (subset), kinds that must NOT fire)

Run after ANY edit to eng_lint.py, section_contract.py, or the templates.
"""
import copy
import pathlib
import re
import subprocess
import sys
import tempfile

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
LINT = PLUGIN / "skills/eng-os/scripts/eng_lint.py"

WORDS_600 = "lorem ipsum dolor sit amet " * 100        # 600 words ≈ 1.15 A4
WORDS_1600 = "lorem ipsum dolor sit amet " * 267       # ≈ 1600 words ≈ 3.05 A4


def clean_tree():
    """The minimal healthy engagement repo: every rule applies, nothing fires."""
    return {
        "CLAUDE.md": (
            "# Repo\n\n"
            "| Topic | File |\n|---|---|\n"
            "| Findings | `02_delivery/1_discovery/3_findings/README.md` |\n"),
        "00_research/README.md": (
            "# Research\n\n## Questions\n\n"
            "1. What is the current refresh cadence? [open]\n"),
        "02_delivery/DELIVERABLES.md": (
            "# Deliverables\n\n"
            "| D | Name | Live file |\n|---|---|---|\n"
            "| D1 | As-is assessment | `02_delivery/2_assessment/d1.md` |\n"),
        "02_delivery/2_assessment/d1.md": "# D1 working notes\n",
        "02_delivery/1_discovery/3_findings/README.md": (
            "# Findings backbone\n\n"
            "The backbone is the eleven limitations named by the buyer.\n"),
        "02_delivery/1_discovery/3_findings/platform/f1.md": (
            "# Finding: single-schema refresh\n\n"
            "Evidence: [Observed] in the query pack.\n\n"
            "Feeds: D1\n"),
        "01_pursuit/27-010/2_analysis/compliance_matrix.md": (
            "# Compliance matrix\n\n"
            "| Req ID | Requirement | Mandatory | Evidence | Status |\n"
            "|---|---|---|---|---|\n"
            "| R-0xx | <requirement> | M / D | <evidence> | <status> |\n"
            "| R-001 | The bidder must do x | M | A-001 | met |\n"
            "| R-002 | The bidder should do y | D | — | n/a |\n"),
        "01_pursuit/_shared/firm_assets.md": (
            "# Firm assets\n\n"
            "| ID | Asset | Date |\n|---|---|---|\n"
            "| A-001 | ACME data platform discovery | 2024-07 |\n"),
        "01_pursuit/27-010/3_drafting/sections/s1.md": (
            "---\n"
            'section: "1.1 Experience"\n'
            'rft_clause: "§5.1.1"\n'
            "marks: 20\n"
            'scoring: "scored as a whole"\n'
            "answers_reqs: [R-001]\n"
            'page_budget: "4 A4, Arial 10 (per section)"\n'
            "figures: [F-01]\n"
            "evidence: [A-001]\n"
            "status: draft\n"
            "---\n\n"
            "# 1.1 Experience\n\n"
            "We did the thing. [RFP §5.1.1]\n\n"
            "![coverage](../figures/F-01_x.png)\n"
            "*Figure 1 — coverage.*\n\n"
            "## Review log\n\n"
            "| Round | Reviewer / lens | Date | Verdict | What changed |\n"
            "|---|---|---|---|---|\n"),
        "01_pursuit/27-010/3_drafting/figures/F-01_x.png": "png",
        "01_pursuit/27-010/3_drafting/figures/F-01_x.html": "<html></html>",
        "01_pursuit/27-010/3_drafting/figures/F-01_x.pptx": "pptx",
        "_sources/public/_md/README.md": (
            "# public pack manifest\n\nNo converted documents yet.\n"),
    }


SEC = "01_pursuit/27-010/3_drafting/sections/s1.md"
MATRIX = "01_pursuit/27-010/2_analysis/compliance_matrix.md"
FINDING = "02_delivery/1_discovery/3_findings/platform/f1.md"
ASSETS = "01_pursuit/_shared/firm_assets.md"


def _sub(t, path, old, new):
    assert old in t[path], f"{path}: pattern not found: {old[:60]}"
    t[path] = t[path].replace(old, new)


def _approve_section(t):
    """status approved + a matching pass verdict (avoids unrelated status warns)."""
    _sub(t, SEC, "status: draft", "status: approved")
    _sub(t, SEC, "|---|---|---|---|---|\n",
         "|---|---|---|---|---|\n| R2 | experienced human | 2026-01-01 | pass | none |\n")


CASES = [
    # ── the clean tree itself ────────────────────────────────────────────────
    ("clean", lambda t: None, set(), set(), set()),

    # ── bucket leak ──────────────────────────────────────────────────────────
    ("leak-absolute",
     lambda t: _sub(t, SEC, "We did the thing.",
                    "We did the thing. See `_sources/engagement/_md/03_dwh/arch.md`."),
     {"bucket-leak"}, set(), set()),
    ("leak-relative",
     lambda t: _sub(t, SEC, "We did the thing.",
                    "We did the thing. See engagement/_md/03_dwh/arch.md for detail."),
     {"bucket-leak"}, set(), set()),
    ("leak-guardrail-is-not-a-leak",
     lambda t: _sub(t, SEC, "We did the thing.",
                    "We did the thing. Nothing in `_sources/engagement/` is reusable."),
     set(), set(), {"bucket-leak"}),

    # ── [⚠VERIFY] in shipped artefacts ───────────────────────────────────────
    ("verify-in-frozen",
     lambda t: (_approve_section(t),
                t.__setitem__("01_pursuit/27-010/4_final/volume2.md",
                              "Final. [⚠VERIFY] this claim.")),
     {"verify-shipped"}, set(), set()),
    ("ds-store-is-not-frozen",
     lambda t: t.__setitem__("01_pursuit/27-010/4_final/.DS_Store", "junk"),
     set(), set(), {"verify-shipped", "frozen-unapproved", "mandatory-open"}),

    # ── mandatory matrix ─────────────────────────────────────────────────────
    ("mandatory-open-frozen",
     lambda t: (_approve_section(t), _sub(t, MATRIX, "| met |", "| open |"),
                t.__setitem__("01_pursuit/27-010/4_final/v.docx", "x")),
     {"mandatory-open"}, set(), set()),
    ("mandatory-open-unfrozen",
     lambda t: _sub(t, MATRIX, "| met |", "| open |"),
     set(), {"mandatory-open"}, set()),
    ("matrix-template-only",
     lambda t: _sub(t, MATRIX, "| R-001 | The bidder must do x | M | A-001 | met |\n"
                    "| R-002 | The bidder should do y | D | — | n/a |\n", ""),
     {"section-req-unknown"}, {"matrix-empty"}, set()),   # the section's R-001 is now unknown too
    ("matrix-template-only-frozen",
     lambda t: (_approve_section(t),
                _sub(t, MATRIX, "| R-001 | The bidder must do x | M | A-001 | met |\n"
                     "| R-002 | The bidder should do y | D | — | n/a |\n", ""),
                t.__setitem__("01_pursuit/27-010/4_final/v.docx", "x")),
     {"matrix-empty", "section-req-unknown"}, set(), set()),
    ("matrix-row-with-literal-lt",      # a real row containing '<' must NOT be skipped
     lambda t: _sub(t, MATRIX, "The bidder must do x", "Keep each limit < 10 pages"),
     set(), set(), set()),              # still met → clean; the point is the row counted
    ("matrix-row-with-lt-open",
     lambda t: (_sub(t, MATRIX, "The bidder must do x", "Keep each limit < 10 pages"),
                _sub(t, MATRIX, "| met |", "| open |")),
     set(), {"mandatory-open"}, set()),

    # ── citations ────────────────────────────────────────────────────────────
    ("dangling-citation",
     lambda t: _sub(t, FINDING, "Evidence:", "See `gone.md §Page 3`.\n\nEvidence:"),
     set(), {"dangling-citation"}, set()),
    ("citation-resolving-only-into-archive",
     lambda t: (t.__setitem__("archived/old/gone.md", "old"),
                _sub(t, FINDING, "Evidence:", "See `gone.md §Page 3`.\n\nEvidence:")),
     set(), {"dangling-citation"}, set()),

    # ── findings ─────────────────────────────────────────────────────────────
    ("finding-untagged",
     lambda t: _sub(t, FINDING, "[Observed]", "seen"),
     {"finding-untagged"}, set(), set()),
    ("finding-tag-only-in-backticks",
     lambda t: _sub(t, FINDING, "[Observed]", "`[Observed]`"),
     {"finding-untagged"}, set(), set()),
    ("finding-feeds-unknown",
     lambda t: _sub(t, FINDING, "Feeds: D1", "Feeds: D9"),
     set(), {"finding-feeds-unknown"}, set()),
    ("findings-empty",
     lambda t: t.pop(FINDING),
     set(), {"findings-empty"}, set()),

    # ── live index / spine ───────────────────────────────────────────────────
    ("live-index-missing",
     lambda t: t.pop("02_delivery/DELIVERABLES.md"),
     set(), {"live-index-missing"}, set()),
    ("spine-placeholder",
     lambda t: _sub(t, "02_delivery/1_discovery/3_findings/README.md",
                    "the eleven limitations", "<label>"),
     set(), {"spine-unfilled"}, set()),

    # ── images & manifest ────────────────────────────────────────────────────
    ("images-untriaged",
     lambda t: (t.__setitem__("_sources/public/_md/doc1/x.md",
                              "# Doc\n\n- `[uncertain]` a chart\n"),
                _sub(t, "_sources/public/_md/README.md", "No converted documents yet.",
                     "| File | Source |\n|---|---|\n| `doc1/x.md` | doc.pdf |")),
     set(), {"images-untriaged"}, set()),
    ("manifest-missing-row",
     lambda t: t.__setitem__("_sources/public/_md/doc1/x.md", "# Doc\n"),
     {"manifest-missing"}, set(), set()),
    ("manifest-absent",
     lambda t: (t.pop("_sources/public/_md/README.md"),
                t.__setitem__("_sources/public/_md/doc1/x.md", "# Doc\n")),
     {"manifest-absent"}, set(), set()),
    ("manifest-stale-row",
     lambda t: _sub(t, "_sources/public/_md/README.md", "No converted documents yet.",
                    "| File | Source |\n|---|---|\n| `doc1/ghost.md` | doc.pdf |"),
     set(), {"manifest-stale-row"}, set()),

    # ── pointer table ────────────────────────────────────────────────────────
    ("pointer-dangling",
     lambda t: _sub(t, "CLAUDE.md", "`02_delivery/1_discovery/3_findings/README.md`",
                    "`02_delivery/nope.md`"),
     {"pointer-dangling"}, set(), set()),

    # ── firm assets ──────────────────────────────────────────────────────────
    ("asset-unknown",
     lambda t: _sub(t, MATRIX, "| R-002 | The bidder should do y | D | — | n/a |",
                    "| R-002 | The bidder should do y | D | A-999 | n/a |"),
     {"asset-unknown"}, set(), set()),
    ("asset-index-missing",
     lambda t: t.pop(ASSETS),
     {"asset-index-missing"}, set(), set()),
    ("asset-in-gaps-is-not-held",
     lambda t: (_sub(t, ASSETS, "| A-001 | ACME data platform discovery | 2024-07 |",
                     "| A-001 | ACME data platform discovery | 2024-07 |\n\n"
                     "## Gaps\n\nA-777 would have been ideal but we don't hold it.\n"),
                _sub(t, MATRIX, "| R-002 | The bidder should do y | D | — | n/a |",
                     "| R-002 | The bidder should do y | D | A-777 | n/a |")),
     {"asset-unknown"}, set(), set()),

    # ── section frontmatter reconciliation ───────────────────────────────────
    ("section-req-unknown",
     lambda t: _sub(t, SEC, "answers_reqs: [R-001]", "answers_reqs: [R-999]"),
     {"section-req-unknown"}, set(), set()),
    ("section-asset-unknown",
     lambda t: _sub(t, SEC, "evidence: [A-001]", "evidence: [A-999]"),
     {"section-asset-unknown"}, set(), set()),
    ("section-figure-unknown",
     lambda t: _sub(t, SEC, "figures: [F-01]", "figures: [F-09]"),
     {"section-figure-unknown"}, {"section-figure-unreferenced"}, set()),
    ("section-figure-undeclared",
     lambda t: _sub(t, SEC, "figures: [F-01]\n", ""),
     set(), {"section-figure-undeclared"}, set()),
    ("section-nofrontmatter",
     lambda t: t.__setitem__(SEC, t[SEC][t[SEC].index("---\n", 4) + 4:]),
     {"section-nofrontmatter"}, set(), set()),

    # ── page budgets ─────────────────────────────────────────────────────────
    ("section-overlength",
     lambda t: (_sub(t, SEC, 'page_budget: "4 A4, Arial 10 (per section)"',
                     'page_budget: "1 A4"'),
                _sub(t, SEC, "We did the thing. [RFP §5.1.1]", WORDS_600)),
     {"section-overlength"}, set(), set()),
    ("shared-pool-different-spellings",   # the regression: dash/case variants must pool
     lambda t: (_sub(t, SEC, 'page_budget: "4 A4, Arial 10 (per section)"',
                     'page_budget: "5 A4 shared across Q1-Q2"'),
                _sub(t, SEC, "We did the thing. [RFP §5.1.1]", WORDS_1600),
                t.__setitem__("01_pursuit/27-010/3_drafting/sections/s2.md",
                              t[SEC].replace("5 A4 shared across Q1-Q2",
                                             "5 A4 Shared across Q1–Q2"))),
     {"section-overlength"}, set(), set()),

    # ── status ↔ review log ──────────────────────────────────────────────────
    ("status-unknown",
     lambda t: _sub(t, SEC, "status: draft", "status: weird"),
     set(), {"status-unknown"}, set()),
    ("status-stale",
     lambda t: _sub(t, SEC, "|---|---|---|---|---|\n",
                    "|---|---|---|---|---|\n| R1 | panel | 2026-01-01 | pass | none |\n"),
     set(), {"status-stale"}, set()),
    ("status-approved-vs-revise",
     lambda t: (_sub(t, SEC, "status: draft", "status: approved"),
                _sub(t, SEC, "|---|---|---|---|---|\n",
                     "|---|---|---|---|---|\n| R1 | panel | 2026-01-01 | revise | none |\n")),
     {"status-contradicts-review"}, set(), set()),
    ("status-reviewed-vs-blocked",
     lambda t: (_sub(t, SEC, "status: draft", "status: reviewed-r1"),
                _sub(t, SEC, "|---|---|---|---|---|\n",
                     "|---|---|---|---|---|\n| R2 | panel | 2026-01-01 | blocked | none |\n")),
     set(), {"status-contradicts-review"}, set()),
    ("verdict-column-found-by-header",    # Verdict not in its usual position
     lambda t: (_sub(t, SEC, "status: draft", "status: reviewed-r1"),
                _sub(t, SEC,
                     "| Round | Reviewer / lens | Date | Verdict | What changed |\n"
                     "|---|---|---|---|---|\n",
                     "| Round | Verdict | Reviewer / lens | Date | What changed |\n"
                     "|---|---|---|---|---|\n"
                     "| R1 | pass | panel | 2026-01-01 | none |\n")),
     set(), set(), {"status-contradicts-review", "status-stale"}),

    # ── freeze gate ──────────────────────────────────────────────────────────
    ("frozen-with-unapproved",
     lambda t: t.__setitem__("01_pursuit/27-010/4_final/v.docx", "x"),
     {"frozen-unapproved"}, set(), set()),
    ("frozen-nested-final",
     lambda t: t.__setitem__("01_pursuit/27-010/4_final/annexes/v.docx", "x"),
     {"frozen-unapproved"}, set(), set()),

    # ── figures on disk ──────────────────────────────────────────────────────
    ("figure-missing",
     lambda t: (_sub(t, SEC, "figures: [F-01]", "figures: [F-01, F-02]"),
                _sub(t, SEC, "![coverage](../figures/F-01_x.png)",
                     "![coverage](../figures/F-01_x.png)\n![team](../figures/F-02_y.png)")),
     {"figure-missing", "section-figure-unknown"}, set(), set()),
    ("figure-not-editable",
     lambda t: (t.pop("01_pursuit/27-010/3_drafting/figures/F-01_x.html"),
                t.pop("01_pursuit/27-010/3_drafting/figures/F-01_x.pptx")),
     set(), {"figure-not-editable"}, set()),
]

KIND_RE = re.compile(r"^\s*(ERROR|warn)\s+\[([\w-]+)\]")


def build(root, files):
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def run_lint(root):
    proc = subprocess.run([sys.executable, str(LINT), str(root)],
                          capture_output=True, text=True)
    errors, warns = set(), set()
    for line in proc.stdout.splitlines():
        m = KIND_RE.match(line)
        if m:
            (errors if m.group(1) == "ERROR" else warns).add(m.group(2))
    return errors, warns, proc.stdout


def main():
    fails = []
    for name, mutate, want_err, want_warn, want_absent in CASES:
        root = pathlib.Path(tempfile.mkdtemp(prefix="engos-lint-"))
        tree = copy.deepcopy(clean_tree())
        mutate(tree)
        build(root, tree)
        errors, warns, out = run_lint(root)
        ok = (errors == want_err and want_warn <= warns
              and not ((errors | warns) & want_absent))
        print(f"  {'✓' if ok else '✗'} {name}")
        if not ok:
            fails.append(name)
            print(f"      errors: got {sorted(errors)} want {sorted(want_err)}")
            print(f"      warns : got {sorted(warns)} want ⊇ {sorted(want_warn)}"
                  + (f" absent {sorted(want_absent)}" if want_absent else ""))
            for line in out.splitlines():
                if KIND_RE.match(line):
                    print(f"        {line.strip()}")

    print(f"\n{len(CASES) - len(fails)}/{len(CASES)} cases pass")
    if fails:
        print(f"✗ FAILING: {fails}")
        return 1
    print("✓ all fixture cases pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
