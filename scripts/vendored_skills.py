#!/usr/bin/env python3
"""vendored_skills.py — deck-craft's skills are copies; forest-skills is the source.

`designing-figures` and `presentation-builder` are written and loaded from forest-skills
(`~/.claude/skills/<name>` symlinks into it). forest-skills is a private repo, so a plugin in
this public marketplace cannot point at it — deck-craft ships a vendored copy instead. A copy
nobody refreshes goes stale silently (deck-craft still said "default output is a PNG" after
forest-skills had moved decks to native PowerPoint), so this script diffs each copy against
its source and, with --sync, overwrites the copy.

    python3 scripts/vendored_skills.py            # check: list drift
    python3 scripts/vendored_skills.py --sync     # make every copy identical to its source

Edit the skill in forest-skills, never here; then --sync and commit both repos.
Source root: $FOREST_SKILLS, default ~/working/forest-skills/skills.
Exit 0 no drift (or source absent: skipped, not passed) · 1 drift found.
"""
import filecmp
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOURCE = Path(os.environ.get("FOREST_SKILLS") or Path.home() / "working" / "forest-skills" / "skills")
VENDORED = {                                    # copy in this repo -> skill name in forest-skills
    "deck-craft/skills/designing-figures": "designing-figures",
    "deck-craft/skills/presentation-builder": "presentation-builder",
}
IGNORE = ["__pycache__", "*.pyc", ".DS_Store"]


def drift(a, b, rel=""):
    """Paths under rel that differ between dirs a and b, or exist in only one."""
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
    if not SOURCE.is_dir():
        print(f"SKIPPED: source {SOURCE} not found (set FOREST_SKILLS) — nothing was checked")
        return 0
    found = 0
    for copy, name in VENDORED.items():
        src, dst = SOURCE / name, REPO / copy
        diffs = drift(src, dst)
        if diffs and sync:
            shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*IGNORE))
            print(f"synced  {copy} <- {src} ({len(diffs)} paths)")
        elif diffs:
            found += 1
            print(f"DRIFT   {copy} vs {src}:\n" + "\n".join(f"          {d}" for d in diffs))
        else:
            print(f"same    {copy}")
    if found:
        print(f"\n{found} vendored skill(s) differ from forest-skills — run with --sync, then commit.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
