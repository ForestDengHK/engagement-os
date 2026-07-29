#!/usr/bin/env python3
"""check_companions.py — which delegated-to skills are actually on this machine.

The pack deliberately delegates: spreadsheets to `xlsx`, documents to `docx`, decks to
`pptx` + `presentation-builder`, figures to `designing-figures`, the review gate to the
Panel Framework. Re-implementing any of them here would be the bug this pack keeps
warning about. The cost of delegating is that a reference can point at nothing — and an
instruction that reads as authoritative but resolves nowhere is worse than no
instruction, because the usual repair is to reimplement the thing locally.

So this answers one question, cheaply and out loud: **what is missing, and what do I
type to get it — or is there nothing to do?**

`engagement-os` deliberately declares NO `dependencies` in its manifest. A declared
dependency that cannot be resolved *disables the dependent plugin* (Claude Code's
`dependency-unsatisfied`), so a hard declaration would mean a user without
`anthropic-agent-skills` added ends up with a dead engagement-os rather than one that
merely cannot recalculate a workbook. The install-everything path is the separate
`consulting-suite` bundle; the skip path is installing `engagement-os` alone. This
script is how you tell which state you are in.

    python3 check_companions.py [--json] [--required-only]

Exit 0 nothing missing, or only recommended companions missing (each has a documented
fallback) · 1 a required companion is missing · 2 could not read the plugin tree.
"""
import argparse
import json
import os
import pathlib
import sys

SUITE_MARKETPLACE = "forest-consulting"
SUITE_REPO = "ForestDengHK/forest-consulting"

# A dependency in a marketplace the user has not added is left unresolved, so the
# `marketplace add` line is part of the instruction, not a footnote to it.
MARKETPLACE_SOURCE = {
    "anthropic-agent-skills": "anthropics/skills",
    "panel-framework": "ForestDengHK/panel-framework",
    SUITE_MARKETPLACE: SUITE_REPO,
}

# name → (level, provided_by, what breaks without it)
# level "required": no documented fallback — the capability is simply absent.
# level "recommended": a fallback is written into the skill that uses it.
COMPANIONS = {
    "xlsx": ("required", f"document-skills@anthropic-agent-skills",
             "eng-estimate cannot recalculate the formula-live workbook; a handed-over "
             "model can ship with #NAME? baked into it"),
    "docx": ("required", f"document-skills@anthropic-agent-skills",
             "eng-render cannot produce the Word deliverable, and eng-bid-respond "
             "cannot fill a client-supplied form in its own layout"),
    "pptx": ("required", f"document-skills@anthropic-agent-skills",
             "deck assembly and OOXML validation are unavailable; verify_deck.py still "
             "runs but has no schema validator to sit behind"),
    "pdf": ("recommended", f"document-skills@anthropic-agent-skills",
            "ingest falls back to pandoc/markitdown extraction"),
    "presentation-builder": ("recommended", f"deck-craft@{SUITE_MARKETPLACE}",
                             "eng-render falls back to a document or markdown output "
                             "instead of a built deck"),
    "designing-figures": ("recommended", f"deck-craft@{SUITE_MARKETPLACE}",
                          "figures are drawn without the archetype pass; expect the "
                          "generic one-row-of-boxes result"),
    "panel-review": ("recommended", "panel-framework@panel-framework",
                     "the review gate stays mandatory but runs as the manual "
                     "multi-lens red-line documented in eng-build-deliverable"),
    "panel-discuss": ("recommended", "panel-framework@panel-framework",
                      "the structure fork is decided without a panel; lock it manually"),
}


def skill_roots():
    """Every directory that can contain `<skill-name>/SKILL.md` on this machine.

    Four layouts are live at once and all of them are legitimate: personal skills, a
    skills-directory plugin, an installed plugin in the versioned cache, and a
    marketplace clone whose plugins sit in the repo itself. Resolving only one of them
    is how a script decides a skill is missing while the user is looking at it.
    """
    home = pathlib.Path.home()
    roots = [home / ".claude" / "skills", pathlib.Path.cwd() / ".claude" / "skills"]
    roots += home.glob(".claude/plugins/cache/*/*/*/skills")
    roots += home.glob(".claude/plugins/marketplaces/*/skills")
    roots += home.glob(".claude/plugins/marketplaces/*/*/skills")
    return [r for r in roots if r.is_dir()]


def find_skill(name, roots=None):
    """Path to `name`'s SKILL.md, or None. Accepts the plugin-root single-skill layout."""
    for root in roots if roots is not None else skill_roots():
        direct = root / name / "SKILL.md"
        if direct.exists():
            return direct
        # A plugin that ships exactly one skill may put SKILL.md at its own root.
        solo = root.parent / "SKILL.md"
        if solo.exists() and f"name: {name}" in solo.read_text(
                encoding="utf-8", errors="replace")[:400]:
            return solo
    return None


def invocation_name(name, path):
    """What you must actually type on THIS machine to invoke `name`.

    The same skill has two different names depending on how it was installed: a personal
    or skills-directory skill is invoked bare, a plugin skill is namespaced under the
    plugin that ships it (`panel-framework:panel-discuss`). Both can be true at once —
    a personal copy and a plugin copy coexist rather than one overriding the other — and
    a doc that hardcodes one form is wrong on every machine holding the other. So the
    name is derived from where the file was found, not assumed.

    `~/.claude/skills/<name>/SKILL.md`                        → bare
    `.../plugins/cache/<marketplace>/<plugin>/<ver>/skills/…`  → `<plugin>:<name>`
    """
    parts = path.parts
    if "cache" in parts:
        i = parts.index("cache")
        if len(parts) > i + 2:
            return f"{parts[i + 2]}:{name}"
    if "marketplaces" in parts:
        i = parts.index("marketplaces")
        # <marketplaces>/<mk>/skills/<name> is the marketplace repo's own layout; the
        # plugin name is the directory between the marketplace and `skills`, when there
        # is one, and otherwise the marketplace-level plugin of the same name.
        if len(parts) > i + 2 and parts[i + 2] != "skills":
            return f"{parts[i + 2]}:{name}"
    return name


def survey():
    roots = skill_roots()
    rows = []
    for name, (level, provider, impact) in COMPANIONS.items():
        found = find_skill(name, roots)
        rows.append({
            "skill": name,
            "level": level,
            "provider": provider,
            "impact": impact,
            "found": str(found.parent) if found else None,
            "invoke_as": invocation_name(name, found) if found else None,
        })
    return rows


def install_lines(missing):
    """The exact commands, deduplicated by the plugin that provides them."""
    providers = []
    for row in missing:
        if row["provider"] not in providers:
            providers.append(row["provider"])
    lines = []
    if any(p.endswith(f"@{SUITE_MARKETPLACE}") for p in providers) or len(providers) > 1:
        lines.append("everything in one step:")
        lines.append(f"    /plugin marketplace add {SUITE_REPO}")
        lines.append(f"    /plugin install consulting-suite@{SUITE_MARKETPLACE}")
        lines.append("")
    lines.append("or only what is missing:")
    for p in providers:
        _, _, mk = p.partition("@")
        repo = MARKETPLACE_SOURCE.get(mk)
        if repo:
            lines.append(f"    /plugin marketplace add {repo}")
        lines.append(f"    /plugin install {p}")
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--required-only", action="store_true",
                    help="ignore companions that have a documented fallback")
    args = ap.parse_args()

    try:
        rows = survey()
    except OSError as exc:
        print(f"  cannot read the plugin tree: {exc}")
        return 2

    if args.required_only:
        rows = [r for r in rows if r["level"] == "required"]
    missing = [r for r in rows if not r["found"]]

    if args.json:
        print(json.dumps({"companions": rows, "missing": [r["skill"] for r in missing],
                          "blocking": [r["skill"] for r in missing
                                       if r["level"] == "required"]}, indent=2))
        return 1 if any(r["level"] == "required" for r in missing) else 0

    print("\nEngagement OS — companion skills\n")
    width = max(len(r["skill"]) for r in rows)
    iwidth = max([len(r["invoke_as"] or "") for r in rows] + [10])
    print(f"    {'skill':<{width}}  {'invoke on this machine as':<{iwidth}}  found in")
    for r in sorted(rows, key=lambda r: (r["found"] is not None, r["skill"])):
        mark = "✓" if r["found"] else ("✗" if r["level"] == "required" else "○")
        where = _shorten(r["found"]) if r["found"] else "NOT INSTALLED"
        print(f"  {mark} {r['skill']:<{width}}  {(r['invoke_as'] or '—'):<{iwidth}}  {where}")

    renamed = [r for r in rows if r["invoke_as"] and r["invoke_as"] != r["skill"]]
    if renamed:
        print("\n  Namespaced here (a plugin skill is invoked under the plugin that ships it,")
        print("  a personal skill bare) — use the middle column, not the bare name:")
        for r in renamed:
            print(f"    {r['skill']} → Skill({r['invoke_as']})")

    if not missing:
        print(f"\n✓ all {len(rows)} companions resolve — nothing to install.")
        print("  Skip the install step; `consulting-suite` would add nothing here.")
        return 0

    blocking = [r for r in missing if r["level"] == "required"]
    print(f"\n{len(missing)} missing ({len(blocking)} required, "
          f"{len(missing) - len(blocking)} recommended):")
    for r in missing:
        print(f"  {r['level']:<12} {r['skill']:<{width}}  {r['impact']}")

    print()
    for line in install_lines(missing):
        print(f"  {line}" if line else "")
    print("\n  Skipping is a supported choice: engagement-os declares no plugin")
    print("  dependencies, so it stays fully installed and enabled either way.")
    return 1 if blocking else 0


def _shorten(path):
    home = str(pathlib.Path.home())
    return path.replace(home, "~") if path.startswith(home) else path


if __name__ == "__main__":
    sys.exit(main())
