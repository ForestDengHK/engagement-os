#!/usr/bin/env python3
"""Scaffold a new consulting engagement repo from the eng-os templates.

Creates the standard directory tree and plants the fill-in-the-blank artefacts with
placeholder substitution. Idempotent: never clobbers a file that already exists.

Usage:
    python scaffold_engagement.py --root <dir> --client <CODE> --eng-id <ID> --name "<name>" [--phase Discovery]

Example:
    python scaffold_engagement.py --root ./acme-27-010 --client ACME --eng-id 27-010 \
        --name "Data Platform Strategic Assessment"
"""
import argparse
import datetime as _dt
import os
import sys

TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")

# Placeholder conventions: DIRS/FILES *path* strings use single-brace tokens ({ENG_ID},
# {CLIENT_LOWER}) resolved by .replace() below; template *body* text uses double-brace tokens
# ({{CLIENT}} etc.) resolved by substitute(). Keep both in mind when editing.

# Empty dirs get a .gitkeep so they survive in git.
DIRS = [
    "01_pursuit/_shared",
    "01_pursuit/{ENG_ID}/1_received",
    "01_pursuit/{ENG_ID}/2_analysis",
    "01_pursuit/{ENG_ID}/3_drafting",
    "01_pursuit/{ENG_ID}/4_final",
    "01_pursuit/{ENG_ID}/5_contracting",
    "01_pursuit/{ENG_ID}/6_contract",
    "01_pursuit/{ENG_ID}/7_briefing",
    "02_delivery/_shared/compliance_research",
    "02_delivery/_shared/{CLIENT_LOWER}_reference/_md/images",
    "02_delivery/0_mobilisation/decks",
    "02_delivery/0_mobilisation/meetings",
    "02_delivery/1_discovery/1_inputs",
    "02_delivery/1_discovery/2_workshops/01_planned",
    "02_delivery/1_discovery/2_workshops/02_held",
    "02_delivery/1_discovery/3_findings/platform",
    "02_delivery/1_discovery/3_findings/data",
    "02_delivery/1_discovery/3_findings/reporting_bi",
    "02_delivery/1_discovery/3_findings/compliance",
    "02_delivery/1_discovery/3_findings/governance",
    "02_delivery/1_discovery/3_findings/operations",
    "02_delivery/1_discovery/3_findings/integration",
    "02_delivery/1_discovery/3_findings/benchmark",
    "02_delivery/1_discovery/4_output",
    "02_delivery/2_assessment",
    "02_delivery/3_target_architecture",
    "02_delivery/4_roadmap",
    "02_delivery/5_cost_model",
    "02_delivery/6_executive_summary",
    "02_delivery/_pm",
    "archived",
    "references/compliance",
    "references/delivery",
    "panel/discussions",
    "panel/drafts",
    "panel/reviews",
    "panel/debriefs",
    ".claude",
]

# (template filename, destination path relative to root)
FILES = [
    ("CLAUDE.md.tmpl", "CLAUDE.md"),
    ("project-context.md.tmpl", ".claude/project-context.md"),
    ("DELIVERABLES.md.tmpl", "02_delivery/DELIVERABLES.md"),
    ("FINDING_STANDARD.md.tmpl", "02_delivery/1_discovery/3_findings/_FINDING_STANDARD.md"),
    ("findings-README.md.tmpl", "02_delivery/1_discovery/3_findings/README.md"),
    ("finding.md.tmpl", "02_delivery/1_discovery/3_findings/_TEMPLATE_finding.md"),
    ("reference-pack-README.md.tmpl", "02_delivery/_shared/{CLIENT_LOWER}_reference/_md/README.md"),
    ("REFERENCE_SUMMARY.md.tmpl", "02_delivery/_shared/{CLIENT_LOWER}_reference/_md/00_REFERENCE_SUMMARY.md"),
    ("REFERENCE_INSIGHTS.md.tmpl", "02_delivery/_shared/{CLIENT_LOWER}_reference/_md/01_REFERENCE_INSIGHTS.md"),
    ("engagement_log.md.tmpl", "02_delivery/_pm/engagement_log.md"),
    ("source_precedence_register.md.tmpl", "02_delivery/_pm/source_precedence_and_conflict_register.md"),
    ("raid_and_decisions.md.tmpl", "02_delivery/_pm/raid_and_decisions.md"),
    ("discovery_questions.md.tmpl", "02_delivery/0_mobilisation/discovery_questions.md"),
    ("SOURCES_GO_HERE.md.tmpl", "02_delivery/_shared/{CLIENT_LOWER}_reference/SOURCES_GO_HERE.md"),
]


def substitute(text, ctx):
    for key, val in ctx.items():
        text = text.replace("{{" + key + "}}", val)
    return text


def write_file(path, content):
    """Write content, never clobbering an existing file."""
    if os.path.exists(path):
        print(f"  skip (exists): {path}")
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  wrote: {path}")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, help="destination directory for the engagement repo")
    ap.add_argument("--client", required=True, help="client short-code, e.g. ACME")
    ap.add_argument("--eng-id", required=True, help="engagement/tender id, e.g. 27-010")
    ap.add_argument("--name", required=True, help="engagement name")
    ap.add_argument("--phase", default="Mobilisation", help="starting phase label")
    args = ap.parse_args()

    ctx = {
        "CLIENT": args.client,
        "CLIENT_LOWER": args.client.lower(),
        "ENG_ID": args.eng_id,
        "ENGAGEMENT_NAME": args.name,
        "DATE": _dt.date.today().isoformat(),
        "PHASE": args.phase,
    }

    root = os.path.abspath(args.root)
    os.makedirs(root, exist_ok=True)
    print(f"Scaffolding engagement into: {root}\n")

    print("Directories:")
    for d in DIRS:
        p = os.path.join(root, substitute(d.replace("{ENG_ID}", ctx["ENG_ID"]).replace("{CLIENT_LOWER}", ctx["CLIENT_LOWER"]), {}))
        os.makedirs(p, exist_ok=True)
        gk = os.path.join(p, ".gitkeep")
        if not os.listdir(p) and not os.path.exists(gk):
            open(gk, "w").close()
    print(f"  {len(DIRS)} directories ensured.\n")

    print("Files:")
    made = 0
    for tmpl, dest in FILES:
        tmpl_path = os.path.join(TEMPLATES, tmpl)
        try:
            with open(tmpl_path, encoding="utf-8") as f:
                body = f.read()
        except FileNotFoundError:
            print(f"  MISSING TEMPLATE: {tmpl_path} (skipped)")
            continue
        dest_path = os.path.join(root, dest.replace("{CLIENT_LOWER}", ctx["CLIENT_LOWER"]))
        if write_file(dest_path, substitute(body, ctx)):
            made += 1

    # Best-effort cross-session memory index in the Claude Code auto-memory dir.
    slug = root.replace("/", "-")
    mem_dir = os.path.expanduser(f"~/.claude/projects/{slug}/memory")
    try:
        mem_tmpl = os.path.join(TEMPLATES, "MEMORY.md.tmpl")
        if os.path.exists(mem_tmpl):
            with open(mem_tmpl, encoding="utf-8") as f:
                mem_body = f.read()
            os.makedirs(mem_dir, exist_ok=True)
            write_file(os.path.join(mem_dir, "MEMORY.md"), substitute(mem_body, ctx))
    except OSError as e:
        print(f"  note: could not create auto-memory index ({e}); create it later if wanted.")

    print(f"\nDone. {made} files planted.\nNext steps:")
    print("  1. Fill .claude/project-context.md (client, scope, stack, stakeholders).")
    print("  2. Set the backbone in 02_delivery/1_discovery/3_findings/README.md.")
    print("  3. Drop client materials under 02_delivery/_shared/%s_reference/ and run `eng-ingest-source`." % ctx["CLIENT_LOWER"])
    print("  4. Run `/panel-init` to stand up the review panel (it will reuse project-context.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
