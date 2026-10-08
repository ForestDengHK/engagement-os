#!/usr/bin/env python3
"""Regression tests for the lint/render defects found running the kernel on a real pursuit.

Each test reproduces one observed failure — on the clean fixture repo from run_tests.py,
mutated, or on a small sections directory for the renderer — so it fails on the code that had
the defect and passes on the fix. Runs under pytest (`python3 -m pytest tests -q`) and as a
script, like the other suites.
"""
import copy
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
import tempfile

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = PLUGIN / "skills/eng-os/scripts"
LINT = SCRIPTS / "eng_lint.py"
RENDER = SCRIPTS / "render_document.py"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The canonical healthy repo ("every rule applies, nothing fires") and its mutation helpers.
rt = _load("run_tests", PLUGIN / "tests/run_tests.py")
lint_mod = _load("eng_lint", LINT)
rd = _load("render_document", RENDER)
sc = _load("section_contract", SCRIPTS / "section_contract.py")
SEC, LOG, MATRIX = rt.SEC, rt.LOG, rt.MATRIX

FINDING_RE = re.compile(r"^\s*(ERROR|warn)\s+\[([\w-]+)\]\s+(\S.*)$")


def lint(tree, *args):
    """Lint `tree` as a fresh repo: ([(level, kind, where, message)], stdout, exit code)."""
    with tempfile.TemporaryDirectory(prefix="engos-fix-") as d:
        root = pathlib.Path(d)
        rt.build(root, tree)
        proc = subprocess.run([sys.executable, str(LINT), str(root), *args],
                              capture_output=True, text=True)
    assert "rule(s) applicable" in proc.stdout, \
        f"lint did not finish (rc={proc.returncode}):\n{proc.stdout}\n{proc.stderr[-2000:]}"
    lines = proc.stdout.splitlines()
    findings = []
    for i, line in enumerate(lines):
        m = FINDING_RE.match(line)
        if m:
            msg = lines[i + 1].strip() if i + 1 < len(lines) else ""
            findings.append((m.group(1), m.group(2), m.group(3), msg))
    return findings, proc.stdout, proc.returncode


def kinds(findings, level=None):
    return {k for lv, k, _w, _m in findings if level is None or lv == level}


def of(findings, kind):
    return [(lv, w, m) for lv, k, w, m in findings if k == kind]


def totals(stdout):
    return next(line for line in stdout.splitlines() if "rule(s) applicable" in line)


def tree():
    return copy.deepcopy(rt.clean_tree())


def set_status(t, status, verdict):
    """A section status plus the review-log row it must agree with."""
    rt._sub(t, SEC, "status: draft", f"status: {status}")
    rt._sub(t, SEC, "|---|---|---|---|---|\n",
            f"|---|---|---|---|---|\n| R1 | panel red-team | 2026-01-01 | {verdict} | none |\n")


# ── 1 · the research log's status column is found by name ─────────────────────────
# The real log carries `Use in response` AFTER `Status`. Reading the last column as the
# status made every cited row — closed ones included — report `research-row-open`.

REAL_LOG_HEADER = (
    "| # | Serves (Req/theme) | Atomic claim | Fact / inference | Stream | Source type "
    "| Exact source + locator | Published / version | Valid as of | Recheck by | Tag "
    "| Confidence | Status | Use in response |\n"
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n")


def test_research_status_is_read_from_the_status_column_not_the_last_one():
    t = tree()
    t[LOG] = (
        "# Bid research log\n\n" + REAL_LOG_HEADER
        + "| BR-001 | R-001 | The benchmark is 12 weeks | fact | ext | primary "
          "| https://example.org/x §Results | 2026-01-01 | 2026-01-01 | — | `[T3:OWN]` | H "
          "| closed | State the 12-week benchmark. |\n"
          "| BR-002 | R-002 | Referee permission pending | fact | int | internal | A-001 | 2024 "
          "| 2026-01-01 | — | internal | M | open | Do not use until confirmed. |\n")
    findings, out, _ = lint(t)                      # the section's Traceability cites BR-001
    assert "research-row-open" not in kinds(findings), out
    rt._sub(t, SEC, "Benchmark → BR-001.", "Benchmark → BR-001; referee → BR-002.")
    findings, out, _ = lint(t)
    hits = of(findings, "research-row-open")
    assert len(hits) == 1 and "BR-002" in hits[0][2] and "'open'" in hits[0][2], out


def test_research_status_falls_back_to_the_last_column_without_a_status_header():
    with tempfile.TemporaryDirectory() as d:
        log = pathlib.Path(d) / "bid_research_log.md"
        log.write_text("| # | Claim | State |\n|---|---|---|\n"
                       "| BR-001 | x | closed |\n| BR-002 | y | open |\n", encoding="utf-8")
        assert lint_mod.research_log_rows_for(log) == {"BR-001": "closed", "BR-002": "open"}


# ── 2 · second-round research ids (`BR2-01`) are ids ──────────────────────────────
# Only `BR-nnn` was recognised: the round-two rows were dropped from the log silently and
# a citation to one was never resolved — not even when it named no row at all.

ROUND_TWO_ROWS = (
    "| BR2-01 | R-001 | A second-round claim | fact | ext | primary | https://example.org/z §2 "
    "| 2026 | 2026-01-01 | — | `[T3:OWN]` | H | closed |\n"
    "| BR2-02 | R-001 | A second-round claim still open | fact | int | internal | A-001 | 2026 "
    "| 2026-01-01 | — | internal | M | open |\n")


def test_round_research_ids_parse_with_their_round():
    assert lint_mod.research_row_id("BR2-01") == "BR2-01"
    assert lint_mod.research_row_id("`BR2-38`") == "BR2-38"
    assert lint_mod.research_row_id("BR-001") == "BR-001"
    assert lint_mod.research_row_id("br-1") == "BR-001"
    assert lint_mod.research_row_id("#3") == "BR-003"
    assert sc.RESEARCH_ID_RE.findall("BR2-01, BR-014 and log #3") == ["BR2-01", "BR-014"]


def test_round_research_citations_resolve_against_the_log():
    t = tree()
    t[LOG] += ROUND_TWO_ROWS
    rt._sub(t, SEC, "Benchmark → BR-001.", "Benchmark → BR-001; round two → BR2-01.")
    findings, out, _ = lint(t)
    assert not {"research-row-unknown", "research-row-open"} & kinds(findings), out

    unknown = copy.deepcopy(t)
    rt._sub(unknown, SEC, "round two → BR2-01.", "round two → BR2-05.")
    findings, out, _ = lint(unknown)
    hits = of(findings, "research-row-unknown")
    assert [lv for lv, _w, _m in hits] == ["ERROR"] and "BR2-05" in hits[0][2], out

    still_open = copy.deepcopy(t)
    rt._sub(still_open, SEC, "round two → BR2-01.", "round two → BR2-02.")
    findings, out, _ = lint(still_open)
    hits = of(findings, "research-row-open")
    assert len(hits) == 1 and "BR2-02" in hits[0][2], out


# ── 3 · an open mandatory escalates at approval or freeze, not at the first review ──
# Escalating at `reviewed-r1` forced a choice between an honest status and a clean lint:
# 61 errors appeared the moment the real sections were marked reviewed.

def test_open_mandatory_stays_a_warning_while_sections_are_only_reviewed():
    for status in ("reviewed-r1", "reviewed-r2"):
        t = tree()
        rt._sub(t, MATRIX, "| met |", "| open |")
        set_status(t, status, "pass")
        findings, out, _ = lint(t)
        hits = of(findings, "mandatory-open")
        assert hits and all(lv == "warn" for lv, _w, _m in hits), (status, out)


def test_open_mandatory_is_an_error_once_a_section_is_approved_or_a_response_frozen():
    t = tree()
    rt._sub(t, MATRIX, "| met |", "| open |")
    rt._approve_section(t)
    findings, out, _ = lint(t)
    hits = of(findings, "mandatory-open")
    assert hits and all(lv == "ERROR" and "already frozen" not in m
                        for lv, _w, m in hits), out

    t = tree()
    rt._sub(t, MATRIX, "| met |", "| open |")
    t["01_pursuit/27-010/4_final/v.docx"] = "x"
    findings, out, _ = lint(t)
    hits = of(findings, "mandatory-open")
    assert hits and all(lv == "ERROR" and "and a response is already frozen" in m
                        for lv, _w, m in hits), out


# ── 4 · converted donor assets: one image line per file, and a sections-only view ───
# 200+ untriaged figures in converted case studies and prior bids came out as two warnings
# per file and buried the section findings.

DONOR = "01_pursuit/_shared/_md/case-study.md"


def donor_asset(t, n_images):
    placed = "".join(f"*Figure `p{i}.png` — `[caption-needed]`: say what this shows.*\n\n"
                     for i in range(n_images))
    index = "".join(f"- `[uncertain]` ![p{i}.png](images/p{i}.png)\n" for i in range(n_images))
    t[DONOR] = f"# Case study\n\n{placed}## Images extracted — triage these\n\n{index}"
    for i in range(n_images):
        t[f"01_pursuit/_shared/_md/images/p{i}.png"] = "png"
    t["01_pursuit/_shared/_md/README.md"] = "- `case-study.md` — converted from `case-study.pdf`\n"


def test_donor_asset_image_warnings_collapse_to_one_line_per_file():
    t = tree()
    donor_asset(t, 3)
    findings, out, _ = lint(t)
    lines = [(lv, k, m) for lv, k, w, m in findings if w == DONOR]
    assert len(lines) == 1, out
    level, kind, msg = lines[0]
    assert level == "warn" and kind == "images-untriaged", out
    assert msg.startswith("3 images untriaged — donor asset, review only if cited"), out


def test_converted_sources_outside_the_asset_layer_keep_both_image_warnings():
    t = tree()
    t["_sources/public/_md/doc1/x.md"] = (
        "# Doc\n\n- `[uncertain]` a chart\n\n"
        "*Figure `p3_img1.png` — `[caption-needed]`: say what this shows.*\n")
    rt._sub(t, "_sources/public/_md/README.md", "No converted documents yet.",
            "| File | Source |\n|---|---|\n| `doc1/x.md` | doc.pdf |")
    findings, out, _ = lint(t)
    assert {"images-untriaged", "images-uncaptioned"} <= kinds(findings, "warn"), out


def test_scope_sections_reports_only_drafting_and_analysis_findings():
    t = tree()
    donor_asset(t, 3)                                                    # _shared/_md
    rt._sub(t, MATRIX, "| met |", "| open |")                            # 2_analysis
    rt._sub(t, SEC, "We did the thing.", "We did the thing. [⚠VERIFY]")  # 3_drafting
    every, out_every, rc_every = lint(t)
    default, out_default, _ = lint(t, "--scope", "all")
    assert sorted(every) == sorted(default) and totals(out_every) == totals(out_default)
    assert DONOR in {w for _lv, _k, w, _m in every}

    scoped, out, rc = lint(t, "--scope", "sections")
    wheres = [w for _lv, _k, w, _m in scoped]
    assert wheres and all(re.search(r"(?:^|/)(?:3_drafting|2_analysis)/", w) for w in wheres), out
    assert {"verify-open", "mandatory-open"} <= kinds(scoped), out
    n_warn = sum(1 for lv, *_ in scoped if lv == "warn")
    assert f"· {n_warn} warning(s)" in totals(out), out
    assert rc == rc_every, "a view must not change the exit status"


# ── 5 · VERIFY markers in the Internal note are sign-off items, not open body text ──
# The contract puts every open item in the Internal note; counting them as `verify-open`
# made a correctly written section look as if its body carried unresolved facts.

INTERNAL_NOTE = (
    "> **Internal note (stripped at render).** Sign-off: owner Alex Murphy.\n"
    "> 1. Referee availability `[⚠VERIFY — owner: Alex Murphy — referee]`.\n"
    "> 2. Rate hold `[⚠VERIFY — bid lead: rate hold period]`.\n"
    "> 3. Insurance letters for the new policy year `[⚠VERIFY — owner: Sam Kelly: letters\n"
    ">    in hand before submission]`.\n\n")


def test_verify_markers_in_the_internal_note_are_reported_as_verify_internal():
    t = tree()
    rt._sub(t, SEC, "We did the thing.", INTERNAL_NOTE + "We did the thing.")
    findings, out, _ = lint(t)
    assert "verify-open" not in kinds(findings), out
    hits = of(findings, "verify-internal")
    assert len(hits) == 1 and hits[0][0] == "warn" and hits[0][2].startswith("3x"), out


def test_verify_markers_in_body_text_still_raise_verify_open():
    t = tree()
    rt._sub(t, SEC, "We did the thing.",
            INTERNAL_NOTE + "We did the thing for [⚠VERIFY — client name owed].")
    findings, out, _ = lint(t)
    opened, internal = of(findings, "verify-open"), of(findings, "verify-internal")
    assert len(opened) == 1 and opened[0][2].startswith("1x"), out
    assert len(internal) == 1 and internal[0][2].startswith("3x"), out


def test_internal_note_markers_do_not_make_an_approved_section_unshippable():
    t = tree()
    rt._approve_section(t)
    rt._sub(t, SEC, "We did the thing.", INTERNAL_NOTE + "We did the thing.")
    findings, out, _ = lint(t)
    assert "verify-in-shippable" not in kinds(findings), out
    assert of(findings, "verify-internal"), out


# ── 6 · render `--profile draft` ─────────────────────────────────────────────────
# `plain` stripped nothing (a deck manifest carried every scoring note, brief, internal
# note, traceability line and VERIFY marker) and `bid` refused anything below reviewed-r2.

DRAFT_BODY = (
    "# 1.1 Experience\n\n"
    "> **Scoring note.** Scored as a whole.\n\n"
    "> **Writer brief for groups A and B (stripped at render).** Lead with outcomes.\n\n"
    + INTERNAL_NOTE
    + "<!-- drafting comment: keep this under two pages -->\n\n"
    "We did the thing (A-004) and benchmarked it at 12 weeks, per BR-001 and BR2-03.\n"
    "Commitment CA-01 and storyline S-02 hold. Referee: "
    "[⚠VERIFY — owner: Alex Murphy — referee availability].\n"
    "Rate hold: `[⚠VERIFY — bid lead: rate hold period]`. Insurance: [⚠VERIFY].\n\n"
    "> FAR 52.204-21 applies to this contract.\n\n"
    "**Figure source.** `F-01_x.html` is the editable master.\n\n"
    "---\n\n"
    "**Traceability.** Benchmark → BR-001; asset → A-004.\n\n"
    "## Review log\n\n"
    "| Round | Reviewer / lens | Date | Verdict | What changed |\n"
    "|---|---|---|---|---|\n"
    "| R1 | panel red-team | 2026-01-01 | blocked | referee owed |\n")

SCAFFOLDING = ("Scoring note", "Writer brief", "Internal note", "drafting comment", "<!--",
               "Figure source", "Traceability", "Review log", "⚠VERIFY")
IDS = ("A-004", "BR-001", "BR2-03", "CA-01", "S-02")


def section_file(title, status, body):
    return (f'---\nsection: "{title}"\nevidence: [A-004]\nstatus: {status}\n'
            f'blocked_on: "the referee — Alex Murphy"\n---\n\n{body}')


SECTIONS = {
    "01_experience.md": section_file("1.1 Experience", "blocked-r1", DRAFT_BODY),
    "02_team.md": section_file("1.2 Team", "draft",
                               "# 1.2 Team\n\nThe team is named. [⚠VERIFY — owner: Morgan]\n"),
}


def render(*args):
    return subprocess.run([sys.executable, str(RENDER), *args], capture_output=True, text=True)


def sections_dir(d):
    sec = pathlib.Path(d) / "sections"
    sec.mkdir()
    for name, text in SECTIONS.items():
        (sec / name).write_text(text, encoding="utf-8")
    return sec


def test_draft_strips_scaffolding_and_ids_and_turns_markers_into_placeholders():
    text, _n_quotes, placeholders = rd.draft_text(DRAFT_BODY)
    for gone in SCAFFOLDING + IDS:
        assert gone not in text, (gone, text)
    assert "FAR 52.204-21 applies" in text                   # an unlabeled quote is content
    assert "Referee: ⟦TO CONFIRM — Alex Murphy⟧" in text
    assert "Rate hold: ⟦TO CONFIRM — bid lead⟧" in text
    assert "Insurance: ⟦TO CONFIRM⟧" in text
    # the Internal note's own markers went with the note; only body markers are placeholders
    assert placeholders == [("Alex Murphy", "referee availability"),
                            ("bid lead", "rate hold period"), ("", "")]


def test_draft_analyse_builds_at_any_status_and_counts_placeholders():
    with tempfile.TemporaryDirectory() as d:
        proc = render("--sections", str(sections_dir(d)), "--analyse", "--profile", "draft")
    assert proc.returncode == 0, proc.stderr
    assert "profile 'draft': WOULD BUILD (draft: 4 placeholders)" in proc.stdout, proc.stdout


def test_draft_document_build_writes_the_placeholder_list():
    with tempfile.TemporaryDirectory() as d:
        out = pathlib.Path(d) / "out"
        proc = render("--sections", str(sections_dir(d)), "--out", str(out), "--name", "vol",
                      "--to", "md", "--profile", "draft")
        assert proc.returncode == 0, proc.stderr
        doc = (out / "vol.md").read_text(encoding="utf-8")
        listing = (out / "vol.placeholders.md").read_text(encoding="utf-8")
    for gone in SCAFFOLDING + IDS:
        assert gone not in doc, (gone, doc)
    items = [line for line in listing.splitlines() if line.startswith("- ")]
    assert items == ["- 01_experience.md · Alex Murphy · referee availability",
                     "- 01_experience.md · bid lead · rate hold period",
                     "- 01_experience.md · — · —",
                     "- 02_team.md · Morgan · —"], listing


def test_draft_deck_manifest_carries_no_scaffolding():
    with tempfile.TemporaryDirectory() as d:
        out = pathlib.Path(d) / "out"
        proc = render("--sections", str(sections_dir(d)), "--out", str(out), "--name", "vol",
                      "--to", "deck-manifest", "--profile", "draft")
        assert proc.returncode == 0, proc.stderr
        manifest = json.loads((out / "vol.deck-manifest.json").read_text(encoding="utf-8"))
        assert (out / "vol.placeholders.md").exists()
    assert manifest["profile"] == "draft"
    bodies = "\n".join(s["body"] for s in manifest["sections"])
    for gone in SCAFFOLDING + IDS:
        assert gone not in bodies, (gone, bodies)
    assert "⟦TO CONFIRM — Morgan⟧" in bodies


# ── 7 · `blocked_on` is a contract field ─────────────────────────────────────────

def test_blocked_on_is_a_frontmatter_field():
    assert "blocked_on" in sc.FIELDS


def test_blocked_section_without_blocked_on_warns():
    t = tree()
    set_status(t, "blocked-r1", "blocked")
    findings, out, _ = lint(t)
    hits = of(findings, "blocked-on-missing")
    assert len(hits) == 1 and hits[0][0] == "warn", out

    planted = copy.deepcopy(t)       # the template's placeholder is not a reason
    rt._sub(planted, SEC, "status: blocked-r1",
            'status: blocked-r1\nblocked_on: "<the external input and who owes it>"')
    findings, out, _ = lint(planted)
    assert len(of(findings, "blocked-on-missing")) == 1, out


def test_blocked_section_that_names_its_input_is_quiet():
    t = tree()
    set_status(t, "blocked-r1", "blocked")
    rt._sub(t, SEC, "status: blocked-r1",
            'status: blocked-r1\nblocked_on: "referee name — Alex Murphy"')
    findings, out, _ = lint(t)
    assert "blocked-on-missing" not in kinds(findings), out



# ── 8 · a figure is editable through its .html master, and a deck draws it natively ─────────
# The render demanded a `.pptx` per figure after the contract moved to "native in the deck,
# or an editable .html/.pptx companion": every figure with only its HTML master was nagged.

def figure_sections(d, companions):
    """A sections dir with one section and one figure; `companions` are suffixes beside the png."""
    root = pathlib.Path(d)
    sec, figs = root / "sections", root / "figures"
    sec.mkdir()
    figs.mkdir()
    (figs / "F-01_x.png").write_text("png", encoding="utf-8")
    for ext in companions:
        (figs / f"F-01_x{ext}").write_text("master", encoding="utf-8")
    (sec / "01.md").write_text(section_file(
        "1.1 Experience", "draft", "# 1.1 Experience\n\n![coverage](../figures/F-01_x.png)\n"),
        encoding="utf-8")
    return sec


def test_an_html_master_makes_a_figure_editable():
    with tempfile.TemporaryDirectory() as d:
        proc = render("--sections", str(figure_sections(d, [".html"])), "--analyse")
    assert "no editable" not in proc.stdout, proc.stdout


def test_a_png_only_figure_names_the_editable_companion_it_lacks():
    with tempfile.TemporaryDirectory() as d:
        proc = render("--sections", str(figure_sections(d, [])), "--analyse")
    assert "no editable companion (.html/.pptx)" in proc.stdout, proc.stdout
    assert ".pptx sibling" not in proc.stdout, proc.stdout


def test_deck_manifest_is_native_and_carries_the_html_master():
    for companions, master in (([".html"], True), ([], False)):
        with tempfile.TemporaryDirectory() as d:
            out = pathlib.Path(d) / "out"
            proc = render("--sections", str(figure_sections(d, companions)), "--out", str(out),
                          "--name", "vol", "--to", "deck-manifest", "--profile", "draft")
            assert proc.returncode == 0, proc.stderr
            manifest = json.loads((out / "vol.deck-manifest.json").read_text(encoding="utf-8"))
        # under the native policy the deck redraws every figure: no companion nag
        assert "no editable" not in proc.stdout, proc.stdout
        assert manifest["figure_policy"] == "native"
        fig = manifest["sections"][0]["figures"][0]
        assert ("html_master" in fig) is master, fig
        if master:
            assert fig["html_master"].endswith("F-01_x.html"), fig


def test_lint_accepts_either_editable_companion():
    for kept in ("F-01_x.html", "F-01_x.pptx"):
        t = tree()
        other = {"F-01_x.html": "F-01_x.pptx", "F-01_x.pptx": "F-01_x.html"}[kept]
        t.pop(f"01_pursuit/27-010/3_drafting/figures/{other}")
        findings, out, _ = lint(t)
        assert "figure-not-editable" not in kinds(findings), (kept, out)


# ── 9 · second-round research ids (`BR2-01`) are internal ids at every site ──────────────

def test_client_render_deletes_round_two_research_ids():
    text = rd.client_text("Benchmarked at 12 weeks (BR2-03), confirmed via BR2-04 and BR-001.\n",
                          "RFT")
    for gone in ("BR2-03", "BR2-04", "BR-001", "BR2"):
        assert gone not in text, text


def test_round_two_research_id_in_body_prose_is_flagged():
    t = tree()
    rt._sub(t, SEC, "We did the thing.", "We did the thing, benchmarked per BR2-01.")
    findings, out, _ = lint(t)
    hits = of(findings, "internal-id-in-prose")
    assert len(hits) == 1 and "BR2-01" in hits[0][2], out


def test_round_two_research_id_is_method_provenance():
    t = tree()
    t["01_pursuit/27-010/2_analysis/rfp_analysis.md"] = (
        "# Analysis\n\n| # | Their challenge | Best-practice / standard | Method provenance | Proof |\n"
        "|---|---|---|---|---|\n| 1 | resilience | ISO 22301 | BR2-01 | A-001 |\n")
    findings, out, _ = lint(t)
    assert "solution-method-unsourced" not in kinds(findings), out

def main():
    tests = [(n, f) for n, f in list(globals().items()) if n.startswith("test_") and callable(f)]
    fails = []
    for name, fn in tests:
        try:
            fn()
            print(f"  ✓ {name}")
        except Exception as exc:                     # a crash is a failure, not an abort
            fails.append(name)
            print(f"  ✗ {name}\n      {type(exc).__name__}: {str(exc)[:600]}")
    print(f"\n{len(tests) - len(fails)}/{len(tests)} lint/render fix cases pass")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
