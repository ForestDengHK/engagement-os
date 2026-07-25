#!/usr/bin/env python3
"""Scaffold a new consulting engagement repo from the eng-os templates.

Creates the standard directory tree and plants the fill-in-the-blank artefacts with
placeholder substitution. Idempotent: never clobbers a file that already exists.

The tree is assembled from composable BLOCKS, so a repo can be pursuit-only, delivery-only,
a standalone research assignment, or any combination:

    --mode research           core + the research tree
    --mode pursuit            core + the bid tree
    --mode delivery           core + the delivery tree
    --mode pursuit,delivery   both  (same as `full`, the default)

Source material is bucketed by CONSTRAINT, not by phase — public / pre_award / engagement —
so the same rule answers "who may see this" in every mode. Blocks select their buckets:
core always gets `public`; `pursuit` adds `pre_award`; `research` and `delivery` add `engagement`.

Usage:
    python scaffold_engagement.py --root <dir> --client <CODE> --eng-id <ID> --name "<name>" \
        [--mode full] [--phase Discovery]

Example:
    python scaffold_engagement.py --root ./acme-27-010 --client ACME --eng-id 27-010 \
        --name "Data Platform Strategic Assessment" --mode pursuit
"""
import argparse
import datetime as _dt
import os
import re
import sys

TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")

# Placeholder conventions: DIRS/FILES *path* strings use single-brace tokens ({ENG_ID},
# {CLIENT_LOWER}) resolved by expand_path() below; template *body* text uses double-brace tokens
# ({{CLIENT}} etc.) resolved by substitute(). Keep both in mind when editing.

# Templates may fence mode-specific content with <!--IF:pursuit--> … <!--/IF:pursuit-->
# (comma-separated for "any of"). Unselected blocks are stripped; selected blocks are unwrapped.
BLOCK_RE = re.compile(r"[ \t]*<!--IF:([a-z,]+)-->\n(.*?)[ \t]*<!--/IF:\1-->\n", re.S)

BLOCKS = ("research", "pursuit", "delivery")  # core is always built

# Which source buckets a block needs. Buckets are CONSTRAINT classes, not phases: a standalone
# research assignment and a delivery engagement both hold client material under the same
# confidentiality terms, so both use `engagement`.
BLOCK_BUCKETS = {"research": ["engagement"], "pursuit": ["pre_award"], "delivery": ["engagement"]}
CORE_BUCKETS = ["public"]

# Empty dirs get a .gitkeep so they survive in git.
CORE_DIRS = [
    "_pm",
    "archived",
    "references/compliance",
    "references/delivery",
    "panel/discussions",
    "panel/drafts",
    "panel/reviews",
    "panel/debriefs",
    ".claude",
]

RESEARCH_DIRS = [
    "00_research/1_analysis",
    "00_research/2_output",
]

PURSUIT_DIRS = [
    "01_pursuit/_shared",
    "01_pursuit/{ENG_ID}/1_received",
    "01_pursuit/{ENG_ID}/2_analysis",
    "01_pursuit/{ENG_ID}/3_drafting",
    "01_pursuit/{ENG_ID}/4_final",
    "01_pursuit/{ENG_ID}/5_contracting",
    "01_pursuit/{ENG_ID}/6_contract",
    "01_pursuit/{ENG_ID}/7_briefing",
]

DELIVERY_DIRS = [
    "02_delivery/_shared/compliance_research",
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
]

# Per-bucket context for the source-pack trio, so each bucket states its own boundary.
# Buckets are named for the CONSTRAINT on the material ("who may see this"), not for a phase —
# that way the same filing question has the same answer in every mode.
BUCKETS = {
    "public": {
        "BUCKET": "public",
        "BUCKET_LABEL": "Public (unrestricted)",
        "BUCKET_SCOPE": "material we could show anyone — publicly obtainable company information, "
        "sector and regulatory research, published benchmarks and standards. If you would hesitate "
        "to show it to a different client, it does not belong here.",
    },
    "pre_award": {
        "BUCKET": "pre_award",
        "BUCKET_LABEL": "Pre-award (bid-scoped)",
        "BUCKET_SCOPE": "material obtained for a BID before any award — what the buyer issued or "
        "published with the tender, clarification answers, and the market research we gathered "
        "around it. Must stay usable if we lose.",
    },
    "engagement": {
        "BUCKET": "engagement",
        "BUCKET_LABEL": "Engagement-bound (restricted)",
        "BUCKET_SCOPE": "material the client gave us under this engagement's confidentiality terms "
        "— internal architecture docs, system exports, org charts, strategy decks, questionnaires. "
        "Scoped to THIS engagement (a research assignment counts); never reused in a bid, this one "
        "or a later one.",
    },
}


def bucket_dirs(name):
    return [f"_sources/{name}/_md/images"]


def bucket_files(name):
    ctx = BUCKETS[name]
    return [
        ("SOURCES_GO_HERE.md.tmpl", f"_sources/{name}/SOURCES_GO_HERE.md", ctx),
        ("reference-pack-README.md.tmpl", f"_sources/{name}/_md/README.md", ctx),
        ("REFERENCE_SUMMARY.md.tmpl", f"_sources/{name}/_md/00_REFERENCE_SUMMARY.md", ctx),
        ("REFERENCE_INSIGHTS.md.tmpl", f"_sources/{name}/_md/01_REFERENCE_INSIGHTS.md", ctx),
    ]

# (template filename, destination path relative to root, extra context)
CORE_FILES = [
    ("CLAUDE.md.tmpl", "CLAUDE.md", {}),
    ("project-context.md.tmpl", ".claude/project-context.md", {}),
    ("sources-README.md.tmpl", "_sources/README.md", {}),
    ("engagement_log.md.tmpl", "_pm/engagement_log.md", {}),
    ("raid_and_decisions.md.tmpl", "_pm/raid_and_decisions.md", {}),
    ("source_precedence_register.md.tmpl", "_pm/source_precedence_and_conflict_register.md", {}),
]

RESEARCH_FILES = [
    ("research-README.md.tmpl", "00_research/README.md", {}),
]

PURSUIT_FILES = [
    ("rfp_analysis.md.tmpl", "01_pursuit/{ENG_ID}/2_analysis/rfp_analysis.md", {}),
    ("compliance_matrix.md.tmpl", "01_pursuit/{ENG_ID}/2_analysis/compliance_matrix.md", {}),
]

DELIVERY_FILES = [
    ("DELIVERABLES.md.tmpl", "02_delivery/DELIVERABLES.md", {}),
    ("FINDING_STANDARD.md.tmpl", "02_delivery/1_discovery/3_findings/_FINDING_STANDARD.md", {}),
    ("findings-README.md.tmpl", "02_delivery/1_discovery/3_findings/README.md", {}),
    ("finding.md.tmpl", "02_delivery/1_discovery/3_findings/_TEMPLATE_finding.md", {}),
    ("discovery_questions.md.tmpl", "02_delivery/0_mobilisation/discovery_questions.md", {}),
]

DIR_BLOCKS = {"research": RESEARCH_DIRS, "pursuit": PURSUIT_DIRS, "delivery": DELIVERY_DIRS}
FILE_BLOCKS = {"research": RESEARCH_FILES, "pursuit": PURSUIT_FILES, "delivery": DELIVERY_FILES}


def parse_mode(raw):
    """'full' / comma-list of blocks → the set of blocks to build."""
    tokens = [t.strip().lower() for t in raw.split(",") if t.strip()]
    if not tokens:
        raise ValueError("empty --mode")
    selected = set()
    for tok in tokens:
        if tok == "full":
            selected |= {"pursuit", "delivery"}  # the bid→delivery lifecycle
        elif tok in BLOCKS:
            selected.add(tok)
        else:
            raise ValueError(
                "unknown mode %r — expected any of: full, %s (comma-separated)"
                % (tok, ", ".join(BLOCKS))
            )
    if not selected:
        raise ValueError("--mode selected no blocks")
    return selected


def buckets_for(selected):
    """Source buckets the selected blocks need, in fixed order, deduplicated."""
    wanted = list(CORE_BUCKETS)
    for block in BLOCKS:
        if block in selected:
            for b in BLOCK_BUCKETS[block]:
                if b not in wanted:
                    wanted.append(b)
    return wanted


def expand_path(path, ctx):
    return path.replace("{ENG_ID}", ctx["ENG_ID"]).replace("{CLIENT_LOWER}", ctx["CLIENT_LOWER"])


def apply_blocks(text, selected):
    """Keep <!--IF:x--> blocks whose block is selected; strip the rest."""
    def repl(m):
        want = set(m.group(1).split(","))
        return m.group(2) if want & selected else ""
    return BLOCK_RE.sub(repl, text)


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
    ap.add_argument(
        "--mode",
        default="full",
        help="which blocks to build: full (default) | research | pursuit | delivery, "
        "comma-separated to combine (e.g. 'pursuit,delivery')",
    )
    ap.add_argument("--phase", default="Mobilisation", help="starting phase label")
    args = ap.parse_args()

    try:
        selected = parse_mode(args.mode)
    except ValueError as e:
        ap.error(str(e))

    ctx = {
        "CLIENT": args.client,
        "CLIENT_LOWER": args.client.lower(),
        "ENG_ID": args.eng_id,
        "ENGAGEMENT_NAME": args.name,
        "DATE": _dt.date.today().isoformat(),
        "PHASE": args.phase,
        "MODE": ", ".join(b for b in BLOCKS if b in selected),
    }

    buckets = buckets_for(selected)
    ctx["BUCKETS"] = " · ".join(buckets)

    dirs = list(CORE_DIRS)
    files = list(CORE_FILES)
    for b in buckets:
        dirs += bucket_dirs(b)
        files += bucket_files(b)
    for block in BLOCKS:  # fixed order, so output is deterministic
        if block in selected:
            dirs += DIR_BLOCKS[block]
            files += FILE_BLOCKS[block]

    root = os.path.abspath(args.root)
    os.makedirs(root, exist_ok=True)
    print(f"Scaffolding engagement into: {root}")
    print(f"Mode: {ctx['MODE']}   Source buckets: {ctx['BUCKETS']}\n")

    print("Directories:")
    for d in dirs:
        p = os.path.join(root, expand_path(d, ctx))
        os.makedirs(p, exist_ok=True)
        gk = os.path.join(p, ".gitkeep")
        if not os.listdir(p) and not os.path.exists(gk):
            open(gk, "w").close()
    print(f"  {len(dirs)} directories ensured.\n")

    print("Files:")
    made = 0
    claude_md_skipped = False
    for tmpl, dest, extra in files:
        tmpl_path = os.path.join(TEMPLATES, tmpl)
        try:
            with open(tmpl_path, encoding="utf-8") as f:
                body = f.read()
        except FileNotFoundError:
            print(f"  MISSING TEMPLATE: {tmpl_path} (skipped)")
            continue
        dest_path = os.path.join(root, expand_path(dest, ctx))
        body = substitute(apply_blocks(body, selected), dict(ctx, **extra))
        if write_file(dest_path, body):
            made += 1
        elif dest == "CLAUDE.md":
            claude_md_skipped = True

    # Best-effort cross-session memory index in the Claude Code auto-memory dir.
    slug = root.replace("/", "-")
    mem_dir = os.path.expanduser(f"~/.claude/projects/{slug}/memory")
    try:
        mem_tmpl = os.path.join(TEMPLATES, "MEMORY.md.tmpl")
        if os.path.exists(mem_tmpl):
            with open(mem_tmpl, encoding="utf-8") as f:
                mem_body = f.read()
            os.makedirs(mem_dir, exist_ok=True)
            write_file(os.path.join(mem_dir, "MEMORY.md"),
                       substitute(apply_blocks(mem_body, selected), ctx))
    except OSError as e:
        print(f"  note: could not create auto-memory index ({e}); create it later if wanted.")

    print(f"\nDone. {made} files planted.")
    if claude_md_skipped and made:
        # Adding a block to an existing repo: the mode-aware files were already written on the
        # first run and are never clobbered, so their block-specific rows must be added by hand.
        print(
            "\n  ⚠ CLAUDE.md already existed and was NOT rewritten. If this run ADDED a block,\n"
            "    extend its pointer table + pipeline-skills list for the new block by hand\n"
            "    (or via `eng-maintain-memory`) — the scaffolder will not do it for you."
        )
    print("\nNext steps:")
    step = 1
    print(f"  {step}. Fill .claude/project-context.md (client, scope, stack, stakeholders).")
    step += 1
    print(f"  {step}. Read _sources/README.md — which bucket each incoming document belongs in "
          f"({ctx['BUCKETS']}).")
    step += 1
    if "research" in selected:
        print(f"  {step}. Write the research questions + scope in 00_research/README.md.")
        step += 1
    if "pursuit" in selected:
        print(f"  {step}. Ingest the tender pack to 01_pursuit/{ctx['ENG_ID']}/1_received/_md/, "
              "then run `eng-rfp-analyze`.")
        step += 1
    if "delivery" in selected:
        print(f"  {step}. Set the backbone in 02_delivery/1_discovery/3_findings/README.md.")
        step += 1
    print(f"  {step}. Drop source materials in the right _sources/ bucket and run `eng-ingest-source`.")
    step += 1
    print(f"  {step}. Run `/panel-init` to stand up the review panel (it reuses project-context.md).")
    print("\n  Blocks are additive — add a phase later with e.g. `--mode pursuit`; nothing "
          "existing is touched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
