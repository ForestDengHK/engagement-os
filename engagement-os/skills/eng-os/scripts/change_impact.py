#!/usr/bin/env python3
"""Detect manual edits and map them to the engagement artefacts they invalidate.

This is the deterministic engine behind eng-propagate-change. It never rewrites a
judgement-bearing artefact. With --apply it only moves already-reviewed sections
back to a revise state and records why; owning skills do the substantive refresh.

State lives in `_pm/change_impact_state.json`. A checkpoint is a declaration that
the current dependency set has been reconciled and reviewed, not a generic "save".

Usage:
    python3 change_impact.py <root> [--json]
    python3 change_impact.py <root> --apply [--json]
    python3 change_impact.py <root> --checkpoint [--json]
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import section_contract as sc

STATE_REL = pathlib.Path("_pm/change_impact_state.json")
SCHEMA_VERSION = 1
OUTPUT_EXTS = {".docx", ".pdf", ".pptx", ".xlsx"}
FIGURE_EXTS = {".html", ".png", ".pptx"}
REVIEWED = {"reviewed-r1", "reviewed-r2", "approved", "reviewed", "issued"}


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(path.read_bytes())


def relpath(root, path):
    return path.relative_to(root).as_posix()


def is_relevant(root, path):
    """Track maintained artefacts, their projections, and frozen packages."""
    if not path.is_file():
        return False
    rel = path.relative_to(root)
    parts = rel.parts
    if not parts or any(p in {".git", "node_modules", "__pycache__", "archived"} for p in parts):
        return False
    if rel == STATE_REL or path.name.startswith((".", "~$")):
        return False
    if "4_final" in parts:
        return True
    s = rel.as_posix()
    if re.search(r"01_pursuit/[^/]+/2_analysis/"
                 r"(?:rfp_analysis|compliance_matrix|bid_research_log|estimation)\.(?:md|xlsx)$",
                 s):
        return True
    if s == "01_pursuit/_shared/firm_assets.md":
        return True
    if re.search(r"01_pursuit/[^/]+/3_drafting/(?:sections|figures)/", s):
        return path.suffix.lower() in {".md", *FIGURE_EXTS}
    if re.search(r"01_pursuit/[^/]+/3_drafting/bid_response_outline\.md$", s):
        # the outline is a maintained SOURCE: its format table drives the render, and
        # untracked, a re-render after an outline edit read as a hand-edited output —
        # an error that refused the checkpoint on the normal sequence
        return True
    if re.search(r"01_pursuit/[^/]+/3_drafting/", s) and path.suffix.lower() in OUTPUT_EXTS:
        return True
    if s.startswith("00_research/1_analysis/") and path.suffix.lower() == ".md":
        return True
    if s.startswith("00_research/2_output/"):
        return path.suffix.lower() in {".md", *OUTPUT_EXTS}
    if s.startswith("02_delivery/"):
        return path.suffix.lower() in {".md", *OUTPUT_EXTS}
    return False


def role_of(rel):
    parts = pathlib.PurePosixPath(rel).parts
    name = pathlib.PurePosixPath(rel).name
    if "4_final" in parts:
        return "frozen"
    if name == "estimation.xlsx":
        return "estimate-workbook"
    if name == "estimation.md":
        return "estimate-snapshot"
    if name == "compliance_matrix.md":
        return "compliance-matrix"
    if name == "rfp_analysis.md":
        return "rfp-analysis"
    if name == "firm_assets.md":
        return "firm-assets"
    if name == "bid_research_log.md":
        return "research-log"
    if "sections" in parts and pathlib.PurePosixPath(rel).suffix == ".md":
        return "response-section"
    if "figures" in parts:
        return "figure"
    if name == "bid_response_outline.md":
        return "response-outline"
    if "3_drafting" in parts and "forms" in parts:
        # Filled buyer forms are MAINTAINED artefacts: the xlsx/docx skill edits them in
        # place and there is no upstream source to re-render them from. Classing them as
        # rendered-output made the lint's required fill-the-form workflow a checkpoint
        # blocker — two gates deadlocking the path one of them mandates.
        return "buyer-form"
    if pathlib.PurePosixPath(rel).suffix in OUTPUT_EXTS:
        return "rendered-output"
    if rel.startswith("02_delivery/1_discovery/3_findings/"):
        return "finding"
    if rel.startswith(("00_research/1_analysis/", "00_research/2_output/", "02_delivery/")):
        return "delivery-content"
    return "artefact"


def canonical_section_text(text):
    """Hash reviewable content, excluding lifecycle bookkeeping itself."""
    m = sc.FM_RE.match(text)
    if m:
        kept = []
        for line in m.group(1).splitlines():
            if not re.match(r"^(?:status|reviewed_sha256):", line):
                kept.append(line.rstrip())
        text = "---\n" + "\n".join(kept) + "\n---\n" + text[m.end():]
    text = re.split(r"^##\s+Review log\s*$", text, maxsplit=1, flags=re.M | re.I)[0]
    return re.sub(r"[ \t]+$", "", text, flags=re.M).strip() + "\n"


def list_value(raw):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    if not raw or "<" in raw:
        return set()
    return {v.strip().strip("'\"") for v in raw.split(",") if v.strip()}


def section_record(root, path):
    text = path.read_text(encoding="utf-8", errors="replace")
    meta, body = sc.parse_frontmatter(text)
    dependencies = (
        sc.fm_list(meta, "answers_reqs", sc.REQ_ID_RE)
        | sc.fm_list(meta, "evidence", sc.ASSET_ID_RE)
        | sc.fm_list(meta, "figures", sc.FIG_ID_RE)
        | list_value(meta.get("depends_on", ""))
    )
    dependencies |= {f"BR-{int(n):03d}" for n in re.findall(r"\blog\s*#\s*(\d+)\b", body, re.I)}
    dependencies |= set(sc.RESEARCH_ID_RE.findall(body))
    verdict = sc.latest_verdict(text)
    return {
        "content_sha256": sha256_bytes(canonical_section_text(text).encode("utf-8")),
        "status": meta.get("status", ""),
        "dependencies": sorted(dependencies),
        "latest_review": {"round": verdict[0], "verdict": verdict[1], "date": verdict[2]}
                         if verdict else None,
    }


def finding_feeds(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^Feeds:\s*(.+)$", text, re.M | re.I)
    return sorted(set(re.findall(r"\bD\d+\b", match.group(1), re.I))) if match else []


def deliverable_index(root):
    out = {}
    path = root / "02_delivery/DELIVERABLES.md"
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.search(r"\|\s*(D\d+)\b.*?`([^`]+)`", line, re.I)
        if match:
            out[match.group(1).upper()] = match.group(2)
    return out


def numbered_row_id(cell, prefix):
    """Row id from a register's first cell. `BR-001`, `br-1`, `#3` and `3` all name row 3.

    The template plants bare numbers; every human and every other register in the pack
    writes the prefixed id. Accepting only one of the two forms made a ten-row research log
    read as zero rows — no error, just an entity set that was silently empty, so a changed
    research claim invalidated nothing.
    """
    cell = cell.strip().strip("`*")
    m = re.fullmatch(rf"{prefix}-?0*(\d{{1,3}})", cell, re.I) or re.fullmatch(r"#?(\d{1,3})", cell)
    return f"{prefix}-{int(m.group(1)):03d}" if m else None


def table_entities(path, id_re, prefix=None):
    """Return stable row hashes keyed by an ID found in pipe-table rows."""
    out = {}
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if not line.lstrip().startswith("|") or re.match(r"^\s*\|?[\s:|-]+\|", line):
            continue
        if prefix:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            key = numbered_row_id(cells[0] if cells else "", prefix)
            if not key:
                continue
        else:
            match = id_re.search(line)
            if not match:
                continue
            key = match.group(0)
        normalized = "|".join(c.strip() for c in line.strip().strip("|").split("|"))
        out[key] = sha256_bytes(normalized.encode("utf-8"))
    return out


def heading_section_hash(path, name_pattern):
    """Hash of one numbered-or-not heading's section, located by NAME.

    It was located by hardcoded number ('## 10.'): any renumbering made the hash empty on
    both sides of a checkpoint — edits to the estimate headline became invisible AND a
    permanent spurious impact fired on every workbook change.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"^##\s*\d*\.?\s*{name_pattern}.*$"
                      r"(.*?)(?=^##\s+|\Z)", text, re.M | re.S)
    return sha256_bytes(match.group(0).strip().encode("utf-8")) if match else ""


def snapshot(root):
    root = pathlib.Path(root).resolve()
    files, sections = {}, {}
    entities = {
        "requirements": {},
        "scope": {},
        "assets": {},
        "research": {},
        "analysis_estimate": {},
    }
    feeds = {}
    for path in sorted(p for p in root.rglob("*") if is_relevant(root, p)):
        rel = relpath(root, path)
        files[rel] = {"sha256": sha256_file(path), "role": role_of(rel)}
        if files[rel]["role"] == "response-section":
            sections[rel] = section_record(root, path)
        elif files[rel]["role"] == "delivery-content" and path.suffix.lower() == ".md":
            record = section_record(root, path)
            if record["status"] in sc.ALL_STATUSES:
                sections[rel] = record
        if files[rel]["role"] == "finding":
            feeds[rel] = finding_feeds(path)
        if files[rel]["role"] == "compliance-matrix":
            entities["requirements"].update(table_entities(path, sc.REQ_ID_RE))
        elif files[rel]["role"] == "rfp-analysis":
            entities["scope"].update(table_entities(path, re.compile(r"\bS-\d{2,3}\b")))
            entities["analysis_estimate"][rel + " §estimate"] = heading_section_hash(path, r"Estimate\b")
        elif files[rel]["role"] == "firm-assets":
            entities["assets"].update(table_entities(path, sc.ASSET_ID_RE))
        elif files[rel]["role"] == "research-log":
            entities["research"].update(table_entities(path, re.compile(r"$^"), "BR"))
    return {
        "schema_version": SCHEMA_VERSION,
        "files": files,
        "entities": entities,
        "sections": sections,
        "finding_feeds": feeds,
        "deliverables": deliverable_index(root),
    }


def load_state(root):
    path = pathlib.Path(root).resolve() / STATE_REL
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"invalid": True}
    return data


def changed_map(old, new):
    changes = []
    old_files, new_files = old.get("files", {}), new.get("files", {})
    for rel in sorted(set(old_files) | set(new_files)):
        if rel not in old_files:
            changes.append({"path": rel, "change": "added", "role": new_files[rel]["role"]})
        elif rel not in new_files:
            changes.append({"path": rel, "change": "deleted", "role": old_files[rel]["role"]})
        elif old_files[rel]["sha256"] != new_files[rel]["sha256"]:
            changes.append({"path": rel, "change": "modified", "role": new_files[rel]["role"]})
    return changes


def changed_entities(old, new):
    result = {}
    for kind in ("requirements", "scope", "assets", "research", "analysis_estimate"):
        before = old.get("entities", {}).get(kind, {})
        after = new.get("entities", {}).get(kind, {})
        result[kind] = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    return result


def add_impact(impacts, artifact, action, reason, owner, severity="warning"):
    item = {
        "artifact": artifact,
        "action": action,
        "reason": reason,
        "owner": owner,
        "severity": severity,
    }
    key = (artifact, action, reason)
    if not any((i["artifact"], i["action"], i["reason"]) == key for i in impacts):
        impacts.append(item)


def is_pricing_section(path, record, root):
    deps = set(record.get("dependencies", []))
    if any("estimation" in d.lower() for d in deps):
        return True
    p = root / path
    if not p.exists():
        return False
    text = p.read_text(encoding="utf-8", errors="replace")
    return bool(re.search(r"\b(?:P50|P80|price|pricing|cost base|rate card|contingency)\b", text, re.I))


def scan(root):
    root = pathlib.Path(root).resolve()
    old = load_state(root)
    current = snapshot(root)
    state_path = str(STATE_REL)
    if old is None:
        return {
            "status": "baseline_missing",
            "state_path": state_path,
            "changed_files": [],
            "changed_entities": {},
            "affected_sections": [],
            "impacts": [{
                "artifact": state_path,
                "action": "checkpoint",
                "reason": "no reconciled change baseline exists yet",
                "owner": "engagement-os:eng-propagate-change",
                "severity": "warning",
            }],
            "has_pending": True,
        }
    if old.get("invalid") or old.get("schema_version") != SCHEMA_VERSION:
        return {
            "status": "state_invalid",
            "state_path": state_path,
            "changed_files": [],
            "changed_entities": {},
            "affected_sections": [],
            "impacts": [{
                "artifact": state_path,
                "action": "rebuild checkpoint",
                "reason": "change-impact state is unreadable or uses an unsupported schema",
                "owner": "engagement-os:eng-propagate-change",
                "severity": "error",
            }],
            "has_pending": True,
        }

    changes = changed_map(old, current)
    entities = changed_entities(old, current)
    impacts, affected = [], {}
    roles_changed = {c["role"] for c in changes}
    paths_changed = {c["path"] for c in changes}
    current_sections = current.get("sections", {})
    old_sections = old.get("sections", {})
    source_change = any(c["role"] not in {"frozen", "rendered-output", "estimate-snapshot",
                                          "buyer-form"}
                        for c in changes)

    def affect(section, reason):
        record = current_sections.get(section) or old_sections.get(section, {})
        affected.setdefault(section, {
            "path": section,
            "current_status": record.get("status", ""),
            "required_status": "",
            "reasons": [],
        })
        if reason not in affected[section]["reasons"]:
            affected[section]["reasons"].append(reason)
        status = record.get("status", "")
        if status in REVIEWED:
            affected[section]["required_status"] = (
                sc.revise_status_for(status, delivery=not section.startswith("01_pursuit/"))
                or "revise")

    for c in changes:
        rel, role = c["path"], c["role"]
        if role == "frozen":
            if c["change"] == "added":
                add_impact(
                    impacts, rel, "verify the new package before checkpointing it",
                    "a new frozen version was added; existing versions remain immutable",
                    "engagement-os:eng-check")
            else:
                add_impact(
                    impacts, rel, "restore frozen copy and create a new dated version",
                    f"the frozen package was {c['change']}; submitted evidence is immutable",
                    "engagement-os:eng-propagate-change", "error")
        elif role == "buyer-form" and c["change"] == "deleted":
            add_impact(
                impacts, rel, "restore it, or remove the response_form declaration that names it",
                "a filled buyer form was deleted; the section declaring buyer-form has nothing to submit",
                "engagement-os:eng-bid-respond")
        elif role == "buyer-form":
            pass                        # maintained authoring — filling the form IS the work
        elif role == "rendered-output" and c["change"] == "deleted":
            add_impact(
                impacts, rel, "re-render when the sources are ready",
                "the generated output was deleted; nothing to verify until it is rebuilt",
                "engagement-os:eng-render", "info")
        elif role == "figure" and c["change"] == "deleted":
            pass                        # handled once per figure id below
        elif role == "response-section" and c["change"] == "deleted":
            lost = sorted(x for x in old_sections.get(rel, {}).get("dependencies", [])
                          if x.startswith("R-"))
            add_impact(
                impacts, rel, "restore it or re-map its requirements in the outline",
                ("a response section was deleted; "
                 + (f"it answered {', '.join(lost)}, which are now answered nowhere"
                    if lost else "its requirement coverage went with it")),
                "engagement-os:eng-bid-respond")
        elif role == "rendered-output":
            if source_change:
                add_impact(
                    impacts, rel, "verify this regenerated output against the changed sources",
                    "a rendered output and at least one maintained source changed",
                    "engagement-os:eng-render")
            else:
                add_impact(
                    impacts, rel, "reconcile the edit into its maintained source, then re-render"
                                  " — or, if this IS the re-render (the renderer itself changed), "
                                  "simply checkpoint",
                    "a generated output changed directly; the next render would otherwise lose it",
                    "engagement-os:eng-render", "error")
        elif role == "estimate-snapshot" and "estimate-workbook" not in roles_changed:
            add_impact(
                impacts, rel, "regenerate from estimation.xlsx",
                "the generated snapshot changed without its source workbook",
                "engagement-os:eng-estimate", "error")

    if "estimate-workbook" in roles_changed:
        for rel in sorted(p for p, f in current["files"].items()
                          if f["role"] == "estimate-snapshot"):
            xlsx = root / pathlib.PurePosixPath(rel).with_suffix(".xlsx")
            md = root / rel
            if rel not in paths_changed or (xlsx.exists() and md.stat().st_mtime < xlsx.stat().st_mtime):
                add_impact(impacts, rel, "recalculate and refresh snapshot",
                           "estimation.xlsx changed", "engagement-os:eng-estimate")
        changed_headlines = set(entities["analysis_estimate"])
        for rel in sorted(p for p, f in current["files"].items() if f["role"] == "rfp-analysis"):
            headline = rel + " §estimate"
            if headline not in changed_headlines:
                add_impact(impacts, headline, "refresh estimate headline and price posture",
                           "estimation.xlsx changed", "engagement-os:eng-rfp-analyze")
        for rel, record in current_sections.items():
            if is_pricing_section(rel, record, root):
                affect(rel, "estimation.xlsx changed")

    if entities["scope"]:
        for rel in sorted(p for p, f in current["files"].items()
                          if f["role"] == "estimate-workbook"):
            add_impact(impacts, rel, "re-baseline the estimate",
                       "scope rows changed: " + ", ".join(entities["scope"]),
                       "engagement-os:eng-estimate")
        changed_scope = set(entities["scope"])
        for rel, record in current_sections.items():
            if changed_scope & set(record.get("dependencies", [])):
                affect(rel, "scope changed: " + ", ".join(sorted(changed_scope)))

    changed_req = set(entities["requirements"])
    changed_assets = set(entities["assets"])
    changed_research = set(entities["research"])
    for rel, record in current_sections.items():
        deps = set(record.get("dependencies", []))
        if changed_req & deps:
            affect(rel, "requirements changed: " + ", ".join(sorted(changed_req & deps)))
        if changed_assets & deps:
            affect(rel, "evidence changed: " + ", ".join(sorted(changed_assets & deps)))
        if changed_research & deps:
            affect(rel, "research changed: " + ", ".join(sorted(changed_research & deps)))

    changed_figures = {
        match.group(1)
        for c in changes if c["role"] == "figure"
        for match in [sc.FIG_FILE_RE.match(pathlib.PurePosixPath(c["path"]).name)]
        if match
    }
    for fig in sorted(changed_figures):
        # Which companions of this figure moved in the same batch? A source edit followed by
        # a re-render is the NORMAL sequence; telling the user to regenerate what they have
        # just regenerated is how a gate's output becomes noise you learn to scroll past.
        moved = {pathlib.PurePosixPath(c["path"]).suffix.lower()
                 for c in changes if c["role"] == "figure"
                 and pathlib.PurePosixPath(c["path"]).name.startswith(fig + "_")}
        exported = {".png", ".pptx"} <= moved
        deleted_set = {c["change"] for c in changes if c["role"] == "figure"
                       and pathlib.PurePosixPath(c["path"]).name.startswith(fig + "_")} == {"deleted"}
        for c in changes:
            if c["role"] == "figure" and pathlib.PurePosixPath(c["path"]).suffix == ".html" \
                    and pathlib.PurePosixPath(c["path"]).name.startswith(fig + "_"):
                if deleted_set:
                    add_impact(
                        impacts, c["path"],
                        f"remove {fig} from any section that declares it, or restore the figure",
                        f"{fig} and its exports were deleted", "engagement-os:eng-bid-respond")
                elif exported:
                    add_impact(impacts, c["path"],
                               "confirm the regenerated PNG and PPTX match the new source",
                               f"{fig} source and both exports changed together",
                               "designing-figures", "info")
                else:
                    add_impact(impacts, c["path"], "regenerate PNG and editable PPTX",
                               f"{fig} source changed", "designing-figures")
        for rel, record in current_sections.items():
            if fig in record.get("dependencies", []):
                affect(rel, f"figure changed: {fig}")

    for rel, record in current_sections.items():
        previous = old_sections.get(rel)
        if not previous:
            continue
        if previous.get("content_sha256") != record.get("content_sha256"):
            affect(rel, "section content changed after the last checkpoint")

    for change in (c for c in changes if c["role"] == "finding"):
        feeds = set(current.get("finding_feeds", {}).get(change["path"], []))
        feeds |= set(old.get("finding_feeds", {}).get(change["path"], []))
        indexes = {**old.get("deliverables", {}), **current.get("deliverables", {})}
        for deliverable in sorted(feeds):
            target = indexes.get(deliverable, deliverable)
            if target in current_sections:
                affect(target, f"validated finding changed: {change['path']}")
            else:
                add_impact(
                    impacts, target, "re-validate inputs, rebuild and re-review deliverable",
                    f"{change['path']} changed and feeds {deliverable}",
                    "engagement-os:eng-build-deliverable")

    if any(c["path"].startswith("00_research/1_analysis/") for c in changes):
        for rel, file_record in current["files"].items():
            if not rel.startswith("00_research/2_output/"):
                continue
            if rel in current_sections:
                affect(rel, "research analysis changed")
            elif file_record["role"] in {"delivery-content", "rendered-output"}:
                add_impact(
                    impacts, rel, "rebuild, re-review and re-render research output",
                    "an upstream research analysis changed",
                    "engagement-os:eng-build-deliverable")

    baseline_day = (old.get("recorded_at") or "")[:10]
    for rel, item in affected.items():
        if item["required_status"]:
            # A re-review recorded AFTER the baseline is the author saying they have already
            # done what this gate asks. Repeating the demand verbatim is how a gate's output
            # becomes noise; the outstanding step is then the checkpoint, not another round.
            review = (current_sections.get(rel) or {}).get("latest_review") or {}
            reviewed_since = (review.get("verdict") == "pass"
                              and review.get("date", "") >= baseline_day
                              and item["current_status"] in REVIEWED)
            if reviewed_since:
                add_impact(
                    impacts, rel,
                    f"confirm the {review['round']} re-review covers this change, then checkpoint",
                    "; ".join(item["reasons"]) + f" — re-review recorded {review['date']}",
                    "engagement-os:eng-bid-respond", "info")
            else:
                add_impact(
                    impacts, rel, f"set status to {item['required_status']} and re-review",
                    "; ".join(item["reasons"]), "engagement-os:eng-bid-respond")
        else:
            add_impact(
                impacts, rel, "carry change into the next render",
                "; ".join(item["reasons"]), "engagement-os:eng-render")

    frozen = sorted(p for p, f in current["files"].items() if f["role"] == "frozen")
    if frozen and source_change:
        add_impact(
            impacts, "01_pursuit/*/4_final/", "leave frozen files untouched; build a new version",
            "a maintained upstream artefact changed after a package was frozen",
            "engagement-os:eng-render")

    status = "changes_detected" if changes else "clean"
    return {
        "status": status,
        "state_path": state_path,
        "changed_files": changes,
        "changed_entities": entities,
        "affected_sections": sorted(affected.values(), key=lambda x: x["path"]),
        "impacts": impacts,
        "has_pending": bool(impacts),
    }


def invalidate_section(path, required_status, reasons):
    if not path.exists() or not required_status:
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    meta, _ = sc.parse_frontmatter(text)
    current = meta.get("status", "")
    if current == required_status or current not in REVIEWED:
        return False
    text, n = re.subn(r"^status:\s*\S+.*$", f"status: {required_status}", text,
                      count=1, flags=re.M)
    if not n:
        return False
    reason = "; ".join(reasons).replace("|", "/")
    # Label the row with the round the section actually reached. A hardcoded `R3` on a
    # section that has only ever had R1 reads as two reviews that never happened — and
    # then becomes the "latest verdict" every downstream gate trusts.
    label = sc.round_of(required_status)
    row = (f"| {label} (change-impact) | change-impact gate | "
           f"{dt.date.today().isoformat()} | revise | {reason} |")
    heading = re.search(r"^##\s+Review log\s*$", text, re.M | re.I)
    if heading:
        tail = text[heading.end():]
        lines = tail.splitlines(keepends=True)
        insert_at, saw_table, trailing = 0, False, 0
        for line in lines:
            if line.lstrip().startswith("|"):
                saw_table = True
                # A row the template PLANTED for a round that has not run yet (empty date and
                # verdict) is not history — appending after it would date this row later than
                # rounds that never happened. Insert above the first such placeholder.
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                # `<date>` / `<pass/revise/blocked>` placeholders are as empty as empty
                # cells — the template plants those, and treating them as real dated the
                # change-impact row AFTER rounds that never ran
                vals = [re.sub(r"<[^>]*>", "", c).strip() for c in cells[2:4]]
                if sc.ROUND_LABEL_RE.match(cells[0] if cells else "") and \
                        len(cells) > 3 and not any(vals):
                    break
                insert_at += len(line)
                trailing = 0
            elif saw_table and line.strip():
                break
            else:
                insert_at += len(line)
                trailing += len(line)          # blank lines after the table belong to it
        insert_at -= trailing
        absolute = heading.end() + insert_at
        text = text[:absolute].rstrip("\n") + "\n" + row + "\n" + text[absolute:].lstrip("\n")
    path.write_text(text, encoding="utf-8")
    return True


def apply_invalidations(root, report):
    root = pathlib.Path(root).resolve()
    changed = []
    for section in report.get("affected_sections", []):
        if invalidate_section(root / section["path"], section["required_status"],
                              section["reasons"]):
            changed.append(section["path"])
    return changed


def checkpoint(root):
    root = pathlib.Path(root).resolve()
    previous = load_state(root)
    if previous is not None:
        report = scan(root)
        blockers = [i for i in report.get("impacts", []) if i.get("severity") == "error"]
        if blockers:
            return {
                "status": "checkpoint_refused",
                "state_path": str(STATE_REL),
                "reason": "error-severity impacts cannot be checkpointed",
                "blockers": blockers,
            }
    state = snapshot(root)
    state["recorded_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    path = root / STATE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": "checkpointed", "state_path": str(STATE_REL),
            "tracked_files": len(state["files"]),
            "tracked_sections": len(state["sections"])}


def print_human(report):
    print(f"change impact: {report['status']}")
    if report.get("changed_files"):
        for item in report["changed_files"]:
            print(f"  {item['change']:8} {item['path']}  [{item['role']}]")
    for item in report.get("impacts", []):
        print(f"  {item['severity'].upper():7} {item['artifact']}: {item['action']}")
        print(f"          because {item['reason']} → {item['owner']}")
    if report.get("invalidated_sections"):
        print("  invalidated: " + ", ".join(report["invalidated_sections"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true",
                       help="mechanically move affected reviewed sections to revise")
    group.add_argument("--checkpoint", action="store_true",
                       help="record the current reconciled/reviewed state")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.checkpoint:
        report = checkpoint(args.root)
    else:
        report = scan(args.root)
        if args.apply and report["status"] not in {"baseline_missing", "state_invalid"}:
            report["invalidated_sections"] = apply_invalidations(args.root, report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_human(report)
    return 1 if report.get("status") in {"state_invalid", "checkpoint_refused"} else 0


if __name__ == "__main__":
    sys.exit(main())
