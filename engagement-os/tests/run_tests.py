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
    # The tender pack gets the same anchored-markdown treatment, so it gets the same rules.
    # Its _md/ has no topic subfolders — the converted documents sit directly in it.
    ("images-untriaged in the tender pack itself",
     lambda t: (t.__setitem__("01_pursuit/27-010/1_received/_md/rft.md",
                              "# RFT\n\n- `[uncertain]` the scoring table\n"),
                t.__setitem__("01_pursuit/27-010/1_received/_md/README.md",
                              "| File | Source |\n|---|---|\n| `rft.md` | RFT.pdf |\n")),
     set(), {"images-untriaged"}, set()),
    ("tender pack converted with no manifest",
     lambda t: t.__setitem__("01_pursuit/27-010/1_received/_md/rft.md", "# RFT\n"),
     {"manifest-absent"}, set(), set()),
    # Real tender filenames have spaces — the row reader must match what the writer writes.
    ("manifest row with spaces in the filename",
     lambda t: (t.__setitem__("01_pursuit/27-010/1_received/_md/27-010 - Main RFT.md",
                              "# RFT\n"),
                t.__setitem__("01_pursuit/27-010/1_received/_md/README.md",
                              "- `27-010 - Main RFT.md` — converted from `27-010 - Main RFT.docx`\n")),
     set(), set(), {"manifest-missing", "manifest-absent", "manifest-stale-row"}),
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
    return converter_tests()


def converter_tests():
    """convert_source.update_manifest: the lint manifest rule errors on a converted MD with
    no row, so the converter must write the row itself — else every conversion is a manual
    lint fix. Found on the real GNI pack: 4 MDs, no manifest, no automated path to green.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "convert_source", PLUGIN / "skills/eng-os/scripts/convert_source.py")
    cs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cs)

    root = pathlib.Path(tempfile.mkdtemp(prefix="engos-conv-"))
    pack = root / "01_pursuit/x-001/1_received/_md"
    pack.mkdir(parents=True)
    src = root / "01_pursuit/x-001/1_received/RFT.pdf"
    src.write_text("fake", encoding="utf-8")
    out = pack / "RFT.md"
    out.write_text("# RFT", encoding="utf-8")
    checks = []

    cs.update_manifest(str(out), str(src))                    # 1. creates README + row
    text = (pack / "README.md").read_text(encoding="utf-8")
    checks.append(("creates manifest", "`RFT.md`" in text and "RFT.pdf" in text))

    out2 = pack / "Appendix.md"                               # 2. appends a second row
    out2.write_text("# App", encoding="utf-8")
    cs.update_manifest(str(out2), str(src))
    text = (pack / "README.md").read_text(encoding="utf-8")
    checks.append(("appends row", "`RFT.md`" in text and "`Appendix.md`" in text))

    cs.update_manifest(str(out), str(src))                    # 3. re-conversion: no duplicate
    text = (pack / "README.md").read_text(encoding="utf-8")
    checks.append(("upserts not duplicates", text.count("`RFT.md`") == 1))

    plain = root / "notes/outside.md"                         # 4. outside _md/: no manifest
    plain.parent.mkdir()
    plain.write_text("x", encoding="utf-8")
    cs.update_manifest(str(plain), str(src))
    checks.append(("ignores non-pack output", not (plain.parent / "README.md").exists()))

    for name, ok in checks:
        print(f"  {'✓' if ok else '✗'} converter:{name}")
    manifest_ok = all(ok for _, ok in checks)
    print("✓ converter manifest-writer passes" if manifest_ok
          else "✗ converter manifest-writer FAILING")

    # Scanner identity must be the exact path, never a basename substring. The real GNI
    # tree contains both `1_General_DataMod Quals.pdf` and `others/Quals.pdf`; the latter
    # was silently treated as indexed by the former until this fixture existed.
    scan_root = pathlib.Path(tempfile.mkdtemp(prefix="engos-scan-"))
    shared = scan_root / "01_pursuit/_shared"
    (shared / "case_studies/others").mkdir(parents=True)
    (shared / "contracts_ref").mkdir()
    (shared / "team_structure").mkdir()
    (shared / "case_studies/1_General_DataMod Quals.pdf").write_text("a", encoding="utf-8")
    (shared / "case_studies/others/Quals.pdf").write_text("b", encoding="utf-8")
    (shared / "PTSB SoW.docx").write_text("c", encoding="utf-8")
    (shared / "contracts_ref/PTSB SoW.docx").write_text("c", encoding="utf-8")
    (shared / "team_structure/create_pptx.js").write_text("helper", encoding="utf-8")
    (shared / "case_studies/needed.pdf").write_text("gap", encoding="utf-8")
    (shared / "firm_assets.md").write_text(
        "# Firm assets\n\n"
        "| ID | Asset |\n|---|---|\n"
        "| A-001 | `case_studies/1_General_DataMod Quals.pdf` |\n"
        "| A-002 | `PTSB SoW.docx` |\n\n"
        "## 1b. Handled companion/support files\n\n"
        "| File | Disposition |\n|---|---|\n"
        "| `team_structure/create_pptx.js` | build helper |\n\n"
        "## Gaps — what we do not hold\n\n"
        "The account team should upload `case_studies/needed.pdf`.\n",
        encoding="utf-8")
    _, waiting = cs.scan(scan_root)
    waiting_rel = {p.relative_to(shared).as_posix() for _, p in waiting}
    scan_checks = [
        ("exact path avoids substring collision",
         "case_studies/others/Quals.pdf" in waiting_rel),
        ("same basename in another folder remains visible",
         "contracts_ref/PTSB SoW.docx" in waiting_rel),
        ("indexed exact path is excluded",
         "case_studies/1_General_DataMod Quals.pdf" not in waiting_rel),
        ("handled helper is excluded",
         "team_structure/create_pptx.js" not in waiting_rel),
        ("path mentioned only in gaps is still waiting",
         "case_studies/needed.pdf" in waiting_rel),
    ]
    for name, ok in scan_checks:
        print(f"  {'✓' if ok else '✗'} scanner:{name}")
    scan_ok = all(ok for _, ok in scan_checks)
    print("✓ asset scanner exact-path tests pass" if scan_ok
          else "✗ asset scanner exact-path tests FAILING")

    anchored, heading_count = cs.number_headings(
        "# Executive Summary\n"
        "## 2.1 Timetable\n"
        "### Section 4.2 Relevant Experience\n"
        "## **4.5. DECLARATION OF COMPLIANCE**\n"
        "## <u>5.2. COST EVALUATION</u>\n"
        "## 2026 Outlook\n"
        "## §5.1 Already Anchored\n")
    anchor_checks = [
        ("native decimal clause preserved", "## §2.1 Timetable" in anchored),
        ("native prefixed clause preserved", "### §4.2 Relevant Experience" in anchored),
        ("formatted bold clause detected", "## §4.5 DECLARATION OF COMPLIANCE" in anchored),
        ("formatted underline clause detected", "## §5.2 COST EVALUATION" in anchored),
        ("four-digit year is not a clause", "## Section 6: 2026 Outlook" in anchored),
        ("existing native anchor not doubled", "## §5.1 Already Anchored" in anchored),
        ("all headings counted", heading_count == 7),
    ]
    for name, ok in anchor_checks:
        print(f"  {'✓' if ok else '✗'} anchors:{name}")
    anchors_ok = all(ok for _, ok in anchor_checks)
    print("✓ native-clause anchor tests pass" if anchors_ok
          else "✗ native-clause anchor tests FAILING")

    # Lint and render share one frontmatter parser. The shipped template puts an inline
    # lifecycle comment on `status`; treating it as part of the value made every planted
    # section unknown to the render gate while lint accepted the first token.
    sc_spec = importlib.util.spec_from_file_location(
        "section_contract", PLUGIN / "skills/eng-os/scripts/section_contract.py")
    sc = importlib.util.module_from_spec(sc_spec)
    sc_spec.loader.exec_module(sc)
    meta, _ = sc.parse_frontmatter(
        "---\n"
        'section: "Workstream #2"\n'
        "status: blocked-r1  # draft → reviewed-r1\n"
        "---\n\n# Body\n")
    contract_checks = [
        ("inline comment stripped", meta.get("status") == "blocked-r1"),
        ("hash inside quoted value preserved", meta.get("section") == "Workstream #2"),
    ]

    render_spec = importlib.util.spec_from_file_location(
        "render_document", PLUGIN / "skills/eng-os/scripts/render_document.py")
    render = importlib.util.module_from_spec(render_spec)
    # render_document imports section_contract by module name.
    sys.modules["section_contract"] = sc
    render_spec.loader.exec_module(render)
    sec_dir = scan_root / "sections"
    sec_dir.mkdir()
    (sec_dir / "s.md").write_text(
        "---\nsection: Test\nstatus: reviewed-r2  # lifecycle note\n---\n\n# Test\n",
        encoding="utf-8")
    contract_checks.append(
        ("render uses contract parser", render.discover(str(sec_dir))[0]["status"] == "reviewed-r2"))

    import zipfile
    ref_dir = pathlib.Path(tempfile.mkdtemp(prefix="engos-refdoc-"))
    ref = render.reference_docx("Arial", "10pt", "a4", str(ref_dir))
    with zipfile.ZipFile(ref) as z:
        styles = z.read("word/styles.xml").decode("utf-8")
        document = z.read("word/document.xml").decode("utf-8")
    contract_checks += [
        ("reference enforces Arial 10",
         'w:ascii="Arial"' in styles and 'w:sz w:val="20"' in styles),
        ("reference enforces A4",
         'w:pgSz w:w="11906" w:h="16838"' in document),
    ]

    for name, ok in contract_checks:
        print(f"  {'✓' if ok else '✗'} contract:{name}")
    contract_ok = all(ok for _, ok in contract_checks)
    print("✓ shared frontmatter parser tests pass" if contract_ok
          else "✗ shared frontmatter parser tests FAILING")

    return 0 if manifest_ok and scan_ok and anchors_ok and contract_ok else 1


if __name__ == "__main__":
    sys.exit(main())
