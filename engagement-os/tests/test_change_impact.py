#!/usr/bin/env python3
"""Regression tests for eng-propagate-change's deterministic impact engine."""
import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
ENGINE = PLUGIN / "skills/eng-os/scripts/change_impact.py"
LINT = PLUGIN / "skills/eng-os/scripts/eng_lint.py"

spec = importlib.util.spec_from_file_location("change_impact", ENGINE)
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


def section(title, req, asset, extra="", body="Approved answer."):
    return (
        "---\n"
        f'section: "{title}"\n'
        'rft_clause: "§5"\n'
        "marks: 10\n"
        'scoring: "whole"\n'
        f"answers_reqs: [{req}]\n"
        'page_budget: "4 A4"\n'
        "figures: [F-01]\n"
        f"evidence: [{asset}]\n"
        f"depends_on: [{extra}]\n"
        "status: approved\n"
        "---\n\n"
        f"# {title}\n\n{body}\n\n"
        "![figure](../figures/F-01_x.png)\n\n"
        "## Review log\n\n"
        "| Round | Reviewer / lens | Date | Verdict | What changed |\n"
        "|---|---|---|---|---|\n"
        "| R2 | experienced human | 2026-07-26 | pass | approved |\n"
    )


def delivery_section(title, body):
    return (
        "---\n"
        f'section: "{title}"\n'
        "figures: []\n"
        "evidence: []\n"
        "depends_on: []\n"
        "status: approved\n"
        "---\n\n"
        f"# {title}\n\n{body}\n\n"
        "## Review log\n\n"
        "| Round | Reviewer / lens | Date | Verdict | What changed |\n"
        "|---|---|---|---|---|\n"
        "| R2 | experienced human | 2026-07-26 | pass | approved |\n"
    )


def tree():
    return {
        "CLAUDE.md": "# Test engagement\n",
        "01_pursuit/27-010/2_analysis/compliance_matrix.md": (
            "| Req ID | Requirement | Mandatory | Evidence | Status |\n"
            "|---|---|---|---|---|\n"
            "| R-001 | Price must be explained | M | A-001 | met |\n"
            "| R-002 | Team must be named | M | A-002 | met |\n"),
        "01_pursuit/27-010/2_analysis/rfp_analysis.md": (
            "# Analysis\n\n## 3. Scope\n\n"
            "| S-ID | Scope | Driver |\n|---|---|---|\n"
            "| S-01 | Assess | 5 systems |\n\n"
            "## 11. Estimate & price posture\n\nP50 €100.\n"),
        "01_pursuit/27-010/2_analysis/estimation.xlsx": b"PK-estimate-v1",
        "01_pursuit/27-010/2_analysis/estimation.md": "# generated estimate v1\n",
        "01_pursuit/27-010/2_analysis/bid_research_log.md": (
            "| # | Serves | Claim | Status |\n|---|---|---|---|\n"
            "| 1 | R-001 | Benchmark is 12 weeks | closed |\n"
            "| 2 | R-002 | Named lead required | closed |\n"),
        "01_pursuit/_shared/firm_assets.md": (
            "| ID | Asset | Date |\n|---|---|---|\n"
            "| A-001 | Rate card | 2026-01 |\n"
            "| A-002 | Lead CV | 2026-01 |\n"),
        "01_pursuit/27-010/3_drafting/sections/s1.md":
            section("Pricing", "R-001", "A-001", "estimation.xlsx, BR-001",
                    "Our P50 is €100, based on log #1."),
        "01_pursuit/27-010/3_drafting/sections/s2.md":
            section("Team", "R-002", "A-002", "", "Our lead is named."),
        "01_pursuit/27-010/3_drafting/figures/F-01_x.html": "<html>v1</html>",
        "01_pursuit/27-010/3_drafting/figures/F-01_x.png": b"png-v1",
        "01_pursuit/27-010/3_drafting/figures/F-01_x.pptx": b"PK-pptx-v1",
        "01_pursuit/27-010/3_drafting/bid.docx": b"PK-docx-v1",
        "01_pursuit/27-010/3_drafting/forms/appendix3.docx": b"PK-form-v1",
        "01_pursuit/27-010/3_drafting/bid_response_outline.md": (
            "# Outline\n\n## Submission format (machine-checked)\n\n"
            "| Key | Value |\n|---|---|\n"
            "| volumes | 1 |\n"),
        "01_pursuit/27-010/4_final/submission.pdf": b"pdf-final-v1",
        "02_delivery/DELIVERABLES.md": (
            "| D | Name | Live file |\n|---|---|---|\n"
            "| D1 | Assessment | `02_delivery/2_assessment/d1.md` |\n"),
        "02_delivery/1_discovery/3_findings/platform/f1.md": (
            "# Finding\n\nEvidence: [Observed]\n\nFeeds: D1\n"),
        "02_delivery/2_assessment/d1.md":
            delivery_section("Assessment", "The current finding is reflected."),
        "00_research/1_analysis/q1.md": "# Analysis\n\nThe market is changing.\n",
        "00_research/2_output/report.md":
            delivery_section("Research report", "The market conclusion."),
    }


def build(items=None):
    root = pathlib.Path(tempfile.mkdtemp(prefix="engos-impact-"))
    for rel, content in (items or tree()).items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
    return root


def mutate_text(root, rel, old, new):
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


def affected(report):
    return {x["path"]: x for x in report["affected_sections"]}


def has_action(report, needle):
    return any(needle in (i["artifact"] + " " + i["action"] + " " + i["reason"])
               for i in report["impacts"])


def case_baseline_and_untracked():
    root = build()
    assert ci.scan(root)["status"] == "baseline_missing"
    result = ci.checkpoint(root)
    assert result["tracked_files"] >= 12
    assert ci.scan(root)["status"] == "clean"
    (root / "notes.txt").write_text("untracked scratch", encoding="utf-8")
    assert ci.scan(root)["status"] == "clean"
    state = (root / ci.STATE_REL).read_text(encoding="utf-8")
    assert "Our P50 is" not in state


def case_estimate_propagates_only_pricing():
    root = build()
    ci.checkpoint(root)
    (root / "01_pursuit/27-010/2_analysis/estimation.xlsx").write_bytes(b"PK-estimate-v2")
    report = ci.scan(root)
    a = affected(report)
    assert "01_pursuit/27-010/3_drafting/sections/s1.md" in a
    assert "01_pursuit/27-010/3_drafting/sections/s2.md" not in a
    assert a["01_pursuit/27-010/3_drafting/sections/s1.md"]["required_status"] == "revise-r2"
    assert has_action(report, "refresh snapshot")
    assert has_action(report, "§estimate")
    assert has_action(report, "new version")
    final_before = (root / "01_pursuit/27-010/4_final/submission.pdf").read_bytes()
    changed = ci.apply_invalidations(root, report)
    assert changed == ["01_pursuit/27-010/3_drafting/sections/s1.md"]
    s1 = (root / changed[0]).read_text(encoding="utf-8")
    s2 = (root / "01_pursuit/27-010/3_drafting/sections/s2.md").read_text(encoding="utf-8")
    assert "status: revise-r2" in s1 and "change-impact gate" in s1
    assert "status: approved" in s2
    assert (root / "01_pursuit/27-010/4_final/submission.pdf").read_bytes() == final_before


def case_refreshed_estimate_does_not_claim_stale_derivatives():
    root = build()
    ci.checkpoint(root)
    (root / "01_pursuit/27-010/2_analysis/estimation.xlsx").write_bytes(b"PK-estimate-v2")
    (root / "01_pursuit/27-010/2_analysis/estimation.md").write_text(
        "# generated estimate v2\n", encoding="utf-8")
    mutate_text(root, "01_pursuit/27-010/2_analysis/rfp_analysis.md",
                "P50 €100.", "P50 €101.")
    report = ci.scan(root)
    assert not any(i["artifact"].endswith("estimation.md") and "refresh snapshot" in i["action"]
                   for i in report["impacts"])
    assert not any(i["artifact"].endswith("§estimate") for i in report["impacts"])
    assert "01_pursuit/27-010/3_drafting/sections/s1.md" in affected(report)


def case_entity_routes():
    cases = [
        ("01_pursuit/27-010/2_analysis/compliance_matrix.md",
         "Price must be explained", "Price and tax must be explained", "s1.md", "R-001"),
        ("01_pursuit/_shared/firm_assets.md",
         "Lead CV", "Updated lead CV", "s2.md", "A-002"),
        ("01_pursuit/27-010/2_analysis/bid_research_log.md",
         "Benchmark is 12 weeks", "Benchmark is 14 weeks", "s1.md", "BR-001"),
    ]
    for rel, old, new, section_name, entity in cases:
        root = build()
        ci.checkpoint(root)
        mutate_text(root, rel, old, new)
        report = ci.scan(root)
        matches = [x for x in report["affected_sections"] if x["path"].endswith(section_name)]
        assert len(matches) == 1 and entity in " ".join(matches[0]["reasons"])


def case_scope_and_figure():
    root = build()
    ci.checkpoint(root)
    mutate_text(root, "01_pursuit/27-010/2_analysis/rfp_analysis.md",
                "5 systems", "8 systems")
    report = ci.scan(root)
    assert report["changed_entities"]["scope"] == ["S-01"]
    assert has_action(report, "re-baseline the estimate")

    root = build()
    ci.checkpoint(root)
    mutate_text(root, "01_pursuit/27-010/3_drafting/figures/F-01_x.html", "v1", "v2")
    report = ci.scan(root)
    assert has_action(report, "regenerate PNG")
    assert len(report["affected_sections"]) == 2


def case_delivery_and_research_propagate():
    root = build()
    ci.checkpoint(root)
    mutate_text(root, "02_delivery/1_discovery/3_findings/platform/f1.md",
                "Evidence: [Observed]", "Evidence: [Observed] and [Reported]")
    report = ci.scan(root)
    d1 = affected(report)["02_delivery/2_assessment/d1.md"]
    assert d1["required_status"] == "revise"

    root = build()
    ci.checkpoint(root)
    mutate_text(root, "00_research/1_analysis/q1.md", "changing", "accelerating")
    report = ci.scan(root)
    research = affected(report)["00_research/2_output/report.md"]
    assert research["required_status"] == "revise"


def case_direct_edits_are_not_blessed():
    root = build()
    ci.checkpoint(root)
    mutate_text(root, "01_pursuit/27-010/2_analysis/estimation.md", "v1", "manual")
    report = ci.scan(root)
    assert any(i["severity"] == "error" and "regenerate from estimation.xlsx" in i["action"]
               for i in report["impacts"])
    assert ci.checkpoint(root)["status"] == "checkpoint_refused"

    root = build()
    ci.checkpoint(root)
    (root / "01_pursuit/27-010/3_drafting/bid.docx").write_bytes(b"PK-human-edit")
    report = ci.scan(root)
    assert any(i["severity"] == "error" and "maintained source" in i["action"]
               for i in report["impacts"])
    assert ci.checkpoint(root)["status"] == "checkpoint_refused"

    root = build()
    ci.checkpoint(root)
    (root / "01_pursuit/27-010/4_final/submission.pdf").write_bytes(b"edited-final")
    report = ci.scan(root)
    assert any(i["severity"] == "error" and i["artifact"].endswith("submission.pdf")
               for i in report["impacts"])
    assert ci.checkpoint(root)["status"] == "checkpoint_refused"

    root = build()
    ci.checkpoint(root)
    new_final = root / "01_pursuit/27-010/4_final/submission-v2.pdf"
    new_final.write_bytes(b"verified-new-version")
    report = ci.scan(root)
    assert not any(i["severity"] == "error" for i in report["impacts"])
    assert ci.checkpoint(root)["status"] == "checkpointed"


def case_approved_body_and_checkpoint():
    root = build()
    ci.checkpoint(root)
    mutate_text(root, "01_pursuit/27-010/3_drafting/sections/s2.md",
                "Our lead is named.", "Our lead and deputy are named.")
    report = ci.scan(root)
    s2 = affected(report)["01_pursuit/27-010/3_drafting/sections/s2.md"]
    assert s2["required_status"] == "revise-r2"
    ci.apply_invalidations(root, report)
    # Simulate completed human re-review, then accept the reconciled state.
    mutate_text(root, "01_pursuit/27-010/3_drafting/sections/s2.md",
                "status: revise-r2", "status: approved")
    ci.checkpoint(root)
    assert ci.scan(root)["status"] == "clean"


def case_lint_blocks_pending():
    root = build()
    ci.checkpoint(root)
    (root / "01_pursuit/27-010/2_analysis/estimation.xlsx").write_bytes(b"PK-estimate-v2")
    proc = subprocess.run([sys.executable, str(LINT), str(root), "--strict"],
                          capture_output=True, text=True)
    assert proc.returncode == 1 and "change-impact-pending" in proc.stdout


def case_cli_contract():
    root = build()
    first = subprocess.run(
        [sys.executable, str(ENGINE), str(root), "--checkpoint", "--json"],
        capture_output=True, text=True)
    assert first.returncode == 0
    assert json.loads(first.stdout)["status"] == "checkpointed"
    (root / "01_pursuit/27-010/4_final/submission.pdf").write_bytes(b"tampered")
    refused = subprocess.run(
        [sys.executable, str(ENGINE), str(root), "--checkpoint", "--json"],
        capture_output=True, text=True)
    assert refused.returncode == 1
    assert json.loads(refused.stdout)["status"] == "checkpoint_refused"


def case_research_row_ids_in_either_form():
    """A log written with `BR-001` ids, cited inline as `BR-001`, must route.

    The engine read row ids only as bare integers and section citations only as `log #n`,
    so a ten-row log written the way the rest of the pack writes ids tracked as ZERO
    entities: a changed research claim invalidated nothing, silently.
    """
    items = tree()
    items["01_pursuit/27-010/2_analysis/bid_research_log.md"] = (
        "| # | Serves | Claim | Status |\n|---|---|---|---|\n"
        "| BR-001 | R-001 | Benchmark is 12 weeks | closed |\n"
        "| BR-002 | R-002 | Named lead required | closed |\n")
    items["01_pursuit/27-010/3_drafting/sections/s1.md"] = section(
        "Pricing", "R-001", "A-001", "estimation.xlsx",
        "Our P50 is €100, benchmarked per BR-001.")
    root = build(items)
    ci.checkpoint(root)
    assert json.loads((root / "_pm/change_impact_state.json").read_text()
                      )["entities"]["research"], "BR rows tracked as zero"
    mutate_text(root, "01_pursuit/27-010/2_analysis/bid_research_log.md",
                "Benchmark is 12 weeks", "Benchmark is 14 weeks")
    report = ci.scan(root)
    matches = [x for x in report["affected_sections"] if x["path"].endswith("s1.md")]
    assert len(matches) == 1 and "BR-001" in " ".join(matches[0]["reasons"])


def case_invalidation_keeps_the_round_it_observed():
    """A `reviewed-r1` section sent back goes to `revise-r1`, logged as an R1 row.

    Pushing it to `revise-r2` and appending a row labelled `R3` claimed two review rounds
    that never ran — and the fabricated round then became the 'latest verdict' every
    downstream gate trusts.
    """
    items = tree()
    items["01_pursuit/27-010/3_drafting/sections/s1.md"] = (
        items["01_pursuit/27-010/3_drafting/sections/s1.md"]
        .replace("status: approved", "status: reviewed-r1")
        .replace("| R2 | experienced human | 2026-07-26 | pass | approved |",
                 "| R1 | panel red-team | 2026-07-26 | pass | scores |"))
    root = build(items)
    ci.checkpoint(root)
    mutate_text(root, "01_pursuit/27-010/3_drafting/figures/F-01_x.html", "v1", "v2")
    report = ci.scan(root)
    target = affected(report)["01_pursuit/27-010/3_drafting/sections/s1.md"]
    assert target["required_status"] == "revise-r1", target["required_status"]
    ci.apply_invalidations(root, report)
    text = (root / "01_pursuit/27-010/3_drafting/sections/s1.md").read_text()
    assert "status: revise-r1" in text
    assert "| R1 (change-impact) |" in text and "| R3 |" not in text
    # and the mutated file must be self-consistent under the contract
    lint = subprocess.run([sys.executable, str(LINT), str(root)],
                          capture_output=True, text=True)
    assert "status-contradicts-review" not in lint.stdout


def case_deletions_are_not_edits():
    """Deleting a draft is a real workflow (start the response over) and must read as deletion.

    Deleted outputs asked to be "verified", a deleted figure set asked to be "regenerated", and a
    deleted response section — which takes its requirement coverage with it — produced no impact
    at all.
    """
    root = build()
    ci.checkpoint(root)
    for rel in ("01_pursuit/27-010/3_drafting/sections/s1.md",
                "01_pursuit/27-010/3_drafting/figures/F-01_x.html",
                "01_pursuit/27-010/3_drafting/figures/F-01_x.png",
                "01_pursuit/27-010/3_drafting/figures/F-01_x.pptx",
                "01_pursuit/27-010/3_drafting/bid.docx"):
        (root / rel).unlink()
    report = ci.scan(root)
    assert has_action(report, "restore it or re-map its requirements"), "deleted section silent"
    assert has_action(report, "R-001"), "the lost requirement is not named"
    assert has_action(report, "remove F-01 from any section that declares it")
    assert not has_action(report, "regenerate PNG and editable PPTX")
    assert has_action(report, "re-render when the sources are ready")
    assert not has_action(report, "verify this regenerated output")


def case_recorded_re_review_stops_the_repeat_demand():
    """Once the author records the re-review, the gate asks for a checkpoint, not another round.

    Following the skill exactly — edit, invalidate, re-review, re-render — left the report
    repeating "set status to revise-r1 and re-review" verbatim, which trains a user to ignore it.
    """
    items = tree()
    rel = "01_pursuit/27-010/3_drafting/sections/s1.md"
    items[rel] = items[rel].replace("status: approved", "status: reviewed-r1").replace(
        "| R2 | experienced human | 2026-07-26 | pass | approved |",
        "| R1 | panel red-team | 2026-07-26 | pass | scores |")
    root = build(items)
    ci.checkpoint(root)
    mutate_text(root, rel, "Our P50 is €100", "Our P50 is €120")
    assert has_action(ci.scan(root), "set status to revise-r1 and re-review")

    # the author does what the gate asked: a later round, recorded, with the status restored
    mutate_text(root, rel, "| R1 | panel red-team | 2026-07-26 | pass | scores |",
                "| R1 | panel red-team | 2026-07-26 | pass | scores |\n"
                "| R1 (2nd pass) | panel red-team | 2099-01-01 | pass | price change re-read |")
    report = ci.scan(root)
    assert not has_action(report, "set status to revise-r1 and re-review")
    assert has_action(report, "then checkpoint")
    assert report["has_pending"], "still pending until the checkpoint lands"


def case_change_row_lands_above_unrun_rounds():
    """The appended row must not sit after rows planted for rounds that never ran.

    The section template used to plant empty R2/R3 rows, so every appended row landed last —
    a log that reads R1, R2, R3, then R1 again. The row goes above the first placeholder,
    and the blank line separating the table from the prose survives.
    """
    items = tree()
    rel = "01_pursuit/27-010/3_drafting/sections/s1.md"
    items[rel] = (items[rel]
                  .replace("status: approved", "status: reviewed-r1")
                  .replace("| R2 | experienced human | 2026-07-26 | pass | approved |\n",
                           "| R1 | panel red-team | 2026-07-26 | pass | scores |\n"
                           "| R2 | <named human> | | | |\n"
                           "| R3 | <final read> | | | |\n"
                           "\n**Rounds are not a formality.**\n"))
    root = build(items)
    ci.checkpoint(root)
    mutate_text(root, rel, "Our P50 is €100", "Our P50 is €120")
    ci.apply_invalidations(root, ci.scan(root))
    lines = [l for l in (root / rel).read_text().splitlines() if l.startswith("|")]
    labels = [l.split("|")[1].strip() for l in lines[2:]]
    assert labels == ["R1", "R1 (change-impact)", "R2", "R3"], labels
    assert "|\n\n**Rounds are not a formality.**" in (root / rel).read_text()


def case_regenerated_exports_are_not_renagged():
    """Source edited AND both exports rebuilt is the normal sequence — say 'confirm', not 'redo'."""
    root = build()
    ci.checkpoint(root)
    mutate_text(root, "01_pursuit/27-010/3_drafting/figures/F-01_x.html", "v1", "v2")
    report = ci.scan(root)
    assert has_action(report, "regenerate PNG and editable PPTX")

    root = build()
    ci.checkpoint(root)
    mutate_text(root, "01_pursuit/27-010/3_drafting/figures/F-01_x.html", "v1", "v2")
    (root / "01_pursuit/27-010/3_drafting/figures/F-01_x.png").write_bytes(b"png-v2")
    (root / "01_pursuit/27-010/3_drafting/figures/F-01_x.pptx").write_bytes(b"PK-pptx-v2")
    report = ci.scan(root)
    assert not has_action(report, "regenerate PNG and editable PPTX")
    assert has_action(report, "confirm the regenerated PNG and PPTX")


def case_filled_buyer_forms_are_maintained_not_rendered():
    """The lint REQUIRES filled buyer forms to live in 3_drafting/forms/
    (rule_buyer_forms_filled), but the engine classed everything there as
    'rendered-output': editing one produced an error-severity 'reconcile the edit
    into its maintained source, then re-render' — there IS no maintained source,
    the form IS one — and the checkpoint was refused. Two gates deadlocked the
    exact workflow one of them mandates (found on the real GNI pack)."""
    root = build()
    ci.checkpoint(root)
    (root / "01_pursuit/27-010/3_drafting/forms/appendix3.docx").write_bytes(b"PK-form-v2")
    report = ci.scan(root)
    assert not any(i["severity"] == "error" for i in report["impacts"]), report["impacts"]
    assert not has_action(report, "reconcile the edit")
    # a form edit is not a source change: no re-render nag on built outputs, no frozen nag
    assert not has_action(report, "verify this regenerated output")
    assert not has_action(report, "new version")
    result = ci.checkpoint(root)
    assert result["status"] == "checkpointed", result

    root = build()
    ci.checkpoint(root)
    (root / "01_pursuit/27-010/3_drafting/forms/appendix3.docx").unlink()
    report = ci.scan(root)
    assert has_action(report, "restore it")
    assert not has_action(report, "re-render")


def case_change_row_lands_above_template_placeholder_rows():
    """The current template plants `<date>` / `<pass/revise/blocked>` placeholder cells,
    not empty ones. Treating them as real history dated the change-impact row AFTER rounds
    that never ran — the exact disorder the guard exists to prevent."""
    items = tree()
    rel = "01_pursuit/27-010/3_drafting/sections/s1.md"
    items[rel] = (items[rel]
                  .replace("status: approved", "status: reviewed-r1")
                  .replace("| R2 | experienced human | 2026-07-26 | pass | approved |\n",
                           "| R1 | panel red-team | 2026-07-26 | pass | scores |\n"
                           "| R2 | <named human> | <date> | <pass/revise/blocked> | <what> |\n"
                           "\n**Rounds are not a formality.**\n"))
    root = build(items)
    ci.checkpoint(root)
    mutate_text(root, rel, "Our P50 is €100", "Our P50 is €120")
    report = ci.scan(root)
    ci.apply_invalidations(root, report)
    text = (root / rel).read_text(encoding="utf-8")
    assert text.index("change-impact gate") < text.index("<pass/revise/blocked>")


def case_rerender_after_outline_edit_is_the_normal_sequence():
    """The outline drives the render (its format table). Untracked, a re-render after an
    outline edit read as a hand-edited output — an error that refused the checkpoint on
    exactly the normal sequence (found live: adding the buyer-document-label row)."""
    root = build()
    ci.checkpoint(root)
    mutate_text(root, "01_pursuit/27-010/3_drafting/bid_response_outline.md",
                "| volumes | 1 |", "| volumes | 1 |\n| buyer document label | RFT |")
    (root / "01_pursuit/27-010/3_drafting/bid.docx").write_bytes(b"PK-docx-v2")
    report = ci.scan(root)
    assert has_action(report, "verify this regenerated output")
    assert not has_action(report, "reconcile the edit")
    assert not any(i["severity"] == "error" for i in report["impacts"])
    assert ci.checkpoint(root)["status"] == "checkpointed"


CASES = [
    ("baseline, clean scan, untracked file ignored, hashes only", case_baseline_and_untracked),
    ("estimate change routes pricing only and preserves final", case_estimate_propagates_only_pricing),
    ("refreshed estimate does not re-report refreshed derivatives",
     case_refreshed_estimate_does_not_claim_stale_derivatives),
    ("R/A/BR entity changes route exact sections", case_entity_routes),
    ("scope and figure changes route their owners", case_scope_and_figure),
    ("delivery findings and research analysis reopen outputs", case_delivery_and_research_propagate),
    ("generated/frozen direct edits are rejected", case_direct_edits_are_not_blessed),
    ("approved body edit invalidates then checkpoints clean", case_approved_body_and_checkpoint),
    ("strict lint blocks pending impact", case_lint_blocks_pending),
    ("CLI emits JSON and refuses unsafe checkpoint", case_cli_contract),
    ("research rows route in either id form", case_research_row_ids_in_either_form),
    ("invalidation keeps the round it observed", case_invalidation_keeps_the_round_it_observed),
    ("regenerated figure exports are not re-nagged", case_regenerated_exports_are_not_renagged),
    ("change row lands above rounds that never ran", case_change_row_lands_above_unrun_rounds),
    ("a recorded re-review stops the repeat demand", case_recorded_re_review_stops_the_repeat_demand),
    ("deletions read as deletions, not edits", case_deletions_are_not_edits),
    ("filled buyer forms are maintained, not rendered", case_filled_buyer_forms_are_maintained_not_rendered),
    ("change row lands above template <date> placeholders", case_change_row_lands_above_template_placeholder_rows),
    ("re-render after outline edit is the normal sequence", case_rerender_after_outline_edit_is_the_normal_sequence),
]


def main():
    failures = []
    for name, fn in CASES:
        try:
            fn()
            print(f"  ✓ {name}")
        except Exception as exc:
            failures.append(name)
            print(f"  ✗ {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(CASES) - len(failures)}/{len(CASES)} change-impact cases pass")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
