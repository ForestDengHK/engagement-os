#!/usr/bin/env python3
"""vendored_skills.py — skills this repo ships as copies of another repo's skills.

`designing-figures` and `presentation-builder` are written and loaded from forest-skills
(`~/.claude/skills/<name>` symlinks into it). forest-skills is a private repo, so a plugin in
this public marketplace cannot point at it — deck-craft ships a vendored copy instead. A copy
nobody refreshes goes stale silently (deck-craft still said "default output is a PNG" after
forest-skills had moved decks to native PowerPoint), so this script diffs each copy against
its source and, with --sync, overwrites the copy.

The panel skills and framework-scripts bundled in engagement-os (`skills/eng-os/panel/`, planted
into engagement repos by the scaffolder) are copies of panel-framework, synced the same way.

    python3 scripts/vendored_skills.py            # check: list drift
    python3 scripts/vendored_skills.py --sync     # make every copy identical to its source

Edit the skill in its source repo, never here; then --sync and commit both repos.
Source roots: $FOREST_SKILLS (default ~/working/forest-skills/skills),
$PANEL_FRAMEWORK (default ~/working/panel-framework).
Exit 0 no drift (a missing source root is skipped, not passed) · 1 drift found.
"""
import filecmp
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCES = {
    "forest-skills": Path(os.environ.get("FOREST_SKILLS") or Path.home() / "working" / "forest-skills" / "skills"),
    "panel-framework": Path(os.environ.get("PANEL_FRAMEWORK") or Path.home() / "working" / "panel-framework"),
}
PANEL = "engagement-os/skills/eng-os/panel"
VENDORED = [                                    # (copy in this repo, source repo, path in the source repo)
    ("deck-craft/skills/designing-figures", "forest-skills", "designing-figures"),
    ("deck-craft/skills/presentation-builder", "forest-skills", "presentation-builder"),
    (f"{PANEL}/framework-scripts", "panel-framework", "framework-scripts"),
] + [(f"{PANEL}/skills/{n}", "panel-framework", f"skills/{n}") for n in
     ("panel-discuss", "panel-edit-role", "panel-init", "panel-new-role", "panel-refresh", "panel-review", "panel-roles")]
IGNORE = ["__pycache__", "*.pyc", ".DS_Store"]


def drift(a, b, rel=""):
    """Paths under rel that differ between dirs a and b, or exist in only one."""
    if not b.is_dir():
        return [f"{rel or './'} (copy missing)"]
    c = filecmp.dircmp(a, b, ignore=IGNORE)
    out = [f"{rel}{n} (only in source)" for n in c.left_only] + [f"{rel}{n} (only in copy)" for n in c.right_only]
    out += [f"{rel}{n}" for n in c.common_funny + c.funny_files]
    out += [f"{rel}{n}" for n in c.common_files               # dircmp alone compares shallowly
            if not filecmp.cmp(a / n, b / n, shallow=False)]
    for d in c.common_dirs:
        out += drift(a / d, b / d, f"{rel}{d}/")
    return sorted(out)


def main():
    sync = "--sync" in sys.argv[1:]
    found = 0
    for root in sorted({r for _, r, _ in VENDORED if not SOURCES[r].is_dir()}):
        print(f"SKIPPED: {root} not found at {SOURCES[root]} — its copies were not checked")
    for copy, root, name in VENDORED:
        if not SOURCES[root].is_dir():
            continue
        src, dst = SOURCES[root] / name, REPO / copy
        diffs = drift(src, dst)
        if diffs and sync:
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*IGNORE))
            print(f"synced  {copy} <- {src} ({len(diffs)} paths)")
        elif diffs:
            found += 1
            print(f"DRIFT   {copy} vs {src}:\n" + "\n".join(f"          {d}" for d in diffs))
        else:
            print(f"same    {copy}")
    if found:
        print(f"\n{found} vendored skill(s) differ from their source — run with --sync, then commit.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
