#!/usr/bin/env python3
"""Check an engagement repo against the invariants that are mechanically decidable.

These rules are enforced by prose everywhere else in the pack, which means they hold only as
well as whatever model happened to read that prose. Here they are checks — cheaper, deterministic,
and they don't get less reliable on a smaller model.

Judgment-bearing rules (did we miss a requirement? is this claim defensible? is the backbone the
right backbone?) are NOT here and can't be — those stay with a reviewer.

Usage:
    python3 eng_lint.py [repo-root] [--strict]

    --strict   treat warnings as failures too (use before shipping)

Exit: 0 clean · 1 errors found · 2 repo doesn't look like an engagement repo
"""
import argparse
import os
import pathlib
import re
import sys

EVIDENCE_TAGS = {"[Observed]", "[Reported]", "[Assumed]", "[RFP]"}
TEXT_EXT = {".md", ".txt"}


class Report:
    def __init__(self):
        self.errors, self.warns, self.checks = [], [], 0

    def error(self, rule, where, msg):
        self.errors.append((rule, where, msg))

    def warn(self, rule, where, msg):
        self.warns.append((rule, where, msg))

    def ran(self):
        self.checks += 1


def text_files(root, *rel):
    base = root.joinpath(*rel)
    if not base.exists():
        return []
    return [p for p in base.rglob("*") if p.is_file() and p.suffix in TEXT_EXT]


# ── rules ────────────────────────────────────────────────────────────────────────

#: A leak cites a FILE inside the bucket; a guardrail only names the bucket. Requiring a path
#: segment after `engagement/` separates them, which matters because the pack's own reuse-analysis
#: template ends with "Nothing in `_sources/engagement/` is [reusable]" — a prohibition that the
#: naive substring check reported as the very violation it warns against.
LEAK_RE = re.compile(r"_sources/engagement/\S*[\w.-]")


def rule_bucket_leak(root, r):
    """engagement/ material must never be cited from a bid. The most expensive failure here."""
    r.ran()
    for p in text_files(root, "01_pursuit"):
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if LEAK_RE.search(line):
                r.error("bucket-leak", f"{p.relative_to(root)}:{i}",
                        "bid document cites engagement-bound material — "
                        "source it independently or drop the claim")


def rule_verify_not_shipped(root, r):
    """[⚠VERIFY] must not survive into a frozen/submitted or live-issued artefact."""
    r.ran()
    for rel in ("01_pursuit", "00_research/2_output"):
        for p in text_files(root, rel):
            if rel == "01_pursuit" and "4_final" not in str(p):
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if "⚠VERIFY" in line:
                    r.error("verify-shipped", f"{p.relative_to(root)}:{i}",
                            "unverified claim in a shipped artefact — close it or cut it")


def rule_mandatory_met(root, r):
    """Every Mandatory compliance-matrix row must reach `met` before a response is frozen."""
    matrices = list(root.glob("01_pursuit/*/2_analysis/compliance_matrix.md"))
    if not matrices:
        return
    r.ran()
    for m in matrices:
        frozen = list((m.parent.parent / "4_final").glob("*")) if (m.parent.parent / "4_final").exists() else []
        frozen = [f for f in frozen if f.name != ".gitkeep"]
        for i, line in enumerate(m.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            cells = [c.strip() for c in line.split("|")]
            if len(cells) < 10 or not cells[1].startswith("R-"):
                continue
            if any("<" in c for c in cells) or cells[4] == "M / D":
                continue          # still the planted template row, not a real requirement
            mandatory, status = cells[4], cells[9]
            if mandatory.upper().startswith("M") and status.lower() != "met":
                where = f"{m.relative_to(root)}:{i}"
                msg = f"mandatory requirement {cells[1]} is '{status}', not 'met'"
                (r.error if frozen else r.warn)("mandatory-open", where,
                                                msg + (" — and a response is already frozen" if frozen else ""))


def rule_citations_resolve(root, r):
    """Every `file.md §Page N` citation must point at a file that exists."""
    r.ran()
    pat = re.compile(r"`?([\w./-]+\.md)\s*§\s*(?:Page|Slide|Section|Sheet)\s*\S*")
    for rel in ("00_research", "02_delivery", "01_pursuit"):
        for p in text_files(root, rel):
            body = p.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(body.splitlines(), 1):
                for cited in pat.findall(line):
                    name = os.path.basename(cited)
                    if name.startswith("<") or "<" in cited:
                        continue          # template placeholder
                    if not any(root.rglob(name)):
                        r.warn("dangling-citation", f"{p.relative_to(root)}:{i}",
                               f"cites '{cited}' — no such file in the repo")


def rule_findings_conform(root, r):
    """Every finding needs an evidence tag from the closed set and a backbone mapping."""
    fdir = root / "02_delivery/1_discovery/3_findings"
    if not fdir.exists():
        return
    r.ran()
    for p in fdir.rglob("*.md"):
        if p.name.startswith("_") or p.name == "README.md":
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        if not any(t in body for t in EVIDENCE_TAGS):
            r.error("finding-untagged", str(p.relative_to(root)),
                    f"no evidence tag — expected one of {' '.join(sorted(EVIDENCE_TAGS))}")
        if not re.search(r"^\s*(\*\*)?(Backbone|Maps to|Feeds)(\*\*)?\s*:", body, re.M | re.I):
            r.error("finding-unmapped", str(p.relative_to(root)),
                    "no Backbone:/Maps to:/Feeds: line — every finding maps to the backbone")


def rule_live_index_resolves(root, r):
    """A live-file index must point at files that exist."""
    for idx, pat in ((root / "02_delivery/DELIVERABLES.md", r"`([^`]+\.(?:pptx|xlsx|docx|pdf|md))`"),
                     (root / "00_research/README.md", r"`([^`]+\.(?:pptx|xlsx|docx|pdf|md))`")):
        if not idx.exists():
            continue
        r.ran()
        for i, line in enumerate(idx.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for ref in re.findall(pat, line):
                if "<" in ref or ref.endswith("…") or "…" in ref:
                    continue          # template placeholder
                if not (root / ref).exists() and not any(root.rglob(os.path.basename(ref))):
                    r.warn("dangling-live-file", f"{idx.relative_to(root)}:{i}",
                           f"index points at '{ref}' which doesn't exist")


def rule_spine_filled(root, r):
    """The spine must be real, not the planted placeholder — everything downstream depends on it."""
    checks = [
        (root / "02_delivery/1_discovery/3_findings/README.md", "<label>", "findings backbone"),
        (root / "00_research/README.md", "<the question, answerable and bounded>", "research question list"),
    ]
    for f, placeholder, label in checks:
        if not f.exists():
            continue
        r.ran()
        if placeholder in f.read_text(encoding="utf-8", errors="replace"):
            r.warn("spine-unfilled", str(f.relative_to(root)),
                   f"{label} is still the planted placeholder — "
                   "sourced facts have nothing to map onto")


def rule_images_triaged(root, r):
    """Extracted images start tagged [uncertain]; leaving them there breaks the lossless rule.

    Found by running a real ingest: 52 images came out of four documents and nothing in the
    pack noticed that none of them had been triaged. This is the silent-decay case — the
    conversion "succeeded", so the gap never surfaces on its own.
    """
    for pack in root.glob("_sources/*/_md"):
        r.ran()
        for p in pack.rglob("*.md"):
            if p.parent == pack:          # pack-root trio: the README *documents* the convention
                continue
            n = sum(1 for line in p.read_text(encoding="utf-8", errors="replace").splitlines()
                    if line.lstrip().startswith("- `[uncertain]`"))
            if n:
                r.warn("images-untriaged", str(p.relative_to(root)),
                       f"{n} extracted image(s) still `[uncertain]` — OCR them inline and retag "
                       "`[ocr-done]`, or classify as `[decorative]`/`[content]`")


def rule_manifest_complete(root, r):
    """Every converted MD needs a manifest row, and every manifest row a file.

    The manifest is hand-maintained, so a missed row is invisible: the MD is searchable but
    nothing records where it came from, which is the one thing the manifest exists to hold.
    """
    for pack in root.glob("_sources/*/_md"):
        readme = pack / "README.md"
        if not readme.exists():
            continue
        r.ran()
        listed = set(re.findall(r"`([\w./-]+\.md)`", readme.read_text(encoding="utf-8", errors="replace")))
        listed = {os.path.basename(x) for x in listed}
        for p in pack.rglob("*.md"):
            if p.parent == pack:          # the trio at the pack root isn't manifest content
                continue
            if p.name not in listed:
                r.error("manifest-missing", str(p.relative_to(root)),
                        f"converted MD has no row in {readme.relative_to(root)} — "
                        "its provenance isn't recorded anywhere")


def rule_pointer_table_resolves(root, r):
    """CLAUDE.md's pointer table must point at files that exist.

    This is where an added block breaks things: the scaffolder won't touch an existing
    CLAUDE.md, so the rows for the new block are added by the agent — and a row naming a
    path that was never created sends every later lookup somewhere empty.
    """
    f = root / "CLAUDE.md"
    if not f.exists():
        return
    r.ran()
    for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not line.startswith("| ") or "`" not in line:
            continue
        for ref in re.findall(r"`([\w./_-]+\.md)`", line):
            if not (root / ref).exists():
                r.error("pointer-dangling", f"CLAUDE.md:{i}",
                        f"pointer table names '{ref}', which doesn't exist — "
                        "a block was probably added without topping up the table")


RULES = [rule_bucket_leak, rule_verify_not_shipped, rule_mandatory_met,
         rule_citations_resolve, rule_findings_conform, rule_live_index_resolves,
         rule_spine_filled, rule_images_triaged, rule_manifest_complete,
         rule_pointer_table_resolves]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".", help="engagement repo root (default: cwd)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    if not (root / "_sources").exists() and not (root / "CLAUDE.md").exists():
        print(f"{root} doesn't look like an engagement repo (no _sources/ or CLAUDE.md)")
        return 2

    r = Report()
    for rule in RULES:
        rule(root, r)

    for label, items in (("ERROR", r.errors), ("warn", r.warns)):
        for kind, where, msg in items:
            print(f"  {label:5} [{kind}] {where}\n         {msg}")

    print(f"\n{r.checks} rule(s) applicable · {len(r.errors)} error(s) · {len(r.warns)} warning(s)")
    if not r.errors and not r.warns:
        print("✓ clean")
    if r.errors or (args.strict and r.warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
