#!/usr/bin/env python3
"""End-to-end check that every documented scenario is runnable as its command sequence.

For each scenario in USAGE.md: scaffold the mode, then for each command verify it exists,
resolves to a real playbook, that every `eng-*` skill the playbook names exists, and that
every path the playbook names **for a block this mode built** exists in the scaffolded tree.

Paths belonging to other blocks are expected — playbooks carry per-block routing tables —
so they are only checked against the modes that actually build them.

Usage: python3 verify_scenarios.py [--keep]
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]   # <plugin>/
CMD, PB = ROOT / "commands", ROOT / "skills/eng-os/references/playbooks"
SKILLS = {d.name for d in (ROOT / "skills").iterdir() if d.is_dir()}
SCAFFOLD = ROOT / "skills/eng-os/scripts/scaffold_engagement.py"

# Which top-level path prefixes each block owns. A path is only required to exist when its
# owning block is part of the mode under test.
BLOCK_PREFIXES = {
    "research": ("00_research/",),
    "pursuit": ("01_pursuit/", "_sources/pre_award/"),
    "delivery": ("02_delivery/",),
    "core": ("_pm/", "_sources/README", "_sources/public/"),
}
# `_sources/engagement/` is built by research OR delivery.
SHARED_PREFIX = ("_sources/engagement/", ("research", "delivery"))

# Paths that exist only when the engagement happens to have the thing they hold. The scaffolder
# is right not to create them — an empty `archive-<PRIOR-ID>/` in a repo with no prior bid is the
# same "built a block just in case" noise the modes exist to avoid.
CONDITIONAL = ("01_pursuit/archive-",)

# scenario -> (mode, [commands])   — mirrors USAGE.md
SCENARIOS = {
    "1 research only": ("research", ["eng-new", "eng-source", "eng-sprint"]),
    "2 pursuit only": ("pursuit", ["eng-new", "eng-rfp"]),
    "3 delivery only": ("delivery", ["eng-new", "eng-source", "eng-workshop", "eng-sprint"]),
    "4 bid then deliver": ("full", ["eng-new", "eng-rfp", "eng-source", "eng-workshop", "eng-sprint"]),
    "5 upgrade (pursuit +delivery)": ("pursuit->pursuit,delivery", ["eng-upgrade"]),
    "6 render (standalone)": ("pursuit", ["eng-render"]),
}

PATH_RE = re.compile(r"`((?:_sources|_pm|00_research|01_pursuit|02_delivery)/[\w<>./-]*)`")
SKILL_RE = re.compile(r"`(eng-[a-z-]+)`")


def blocks_of(mode):
    return {"pursuit", "delivery"} if mode == "full" else set(mode.split(","))


def owned_by_selected(path, blocks):
    """Is this path's owning block part of the mode? (unowned paths are never required)"""
    if path.startswith(CONDITIONAL):
        return False
    for block, prefixes in BLOCK_PREFIXES.items():
        if any(path.startswith(p) for p in prefixes):
            return block == "core" or block in blocks
    if path.startswith(SHARED_PREFIX[0]):
        return bool(blocks & set(SHARED_PREFIX[1]))
    return False


def scaffold(root, mode):
    steps = mode.split("->")  # "a->b" = scaffold a, then additively scaffold b
    for step in steps:
        subprocess.run(
            [sys.executable, str(SCAFFOLD), "--root", str(root), "--client", "ACME",
             "--eng-id", "27-010", "--name", "Study", "--mode", step],
            check=True, capture_output=True)
    return blocks_of(steps[-1])


def main():
    keep = "--keep" in sys.argv
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="engos-e2e-"))
    fails = []
    try:
        for name, (mode, cmds) in SCENARIOS.items():
            root = tmp / re.sub(r"[^a-z]+", "_", name)
            blocks = scaffold(root, mode)
            print(f"\n─── {name}   mode={mode}   blocks={sorted(blocks)} ───")
            for c in cmds:
                f = CMD / f"{c}.md"
                if not f.exists():
                    print(f"  ✗ /{c}: command file missing"); fails.append(f"{name}:/{c}"); continue
                text = f.read_text()
                # A command targets either a multi-step playbook or, when it wraps a single
                # capability, one skill directly. Both are legitimate; require one of them.
                m = re.search(r"playbooks/([\w-]+\.md)", text)
                if m and (PB / m.group(1)).exists():
                    target, body = m.group(1), (PB / m.group(1)).read_text()
                else:
                    ms = re.search(r"skills/(eng-[\w-]+)/SKILL\.md", text)
                    if not ms or not (ROOT / "skills" / ms.group(1) / "SKILL.md").exists():
                        print(f"  ✗ /{c}: neither a playbook nor a skill target resolves")
                        fails.append(f"{name}:/{c}"); continue
                    target = ms.group(1)
                    body = (ROOT / "skills" / target / "SKILL.md").read_text()

                missing_skills = sorted(set(SKILL_RE.findall(body)) - SKILLS)
                required = {p for p in PATH_RE.findall(body) if owned_by_selected(p, blocks)}
                bad = []
                for p in sorted(required):
                    # <ENG-ID> is concrete; any other <placeholder> is a naming pattern → glob it.
                    probe = p.replace("<ENG-ID>", "27-010").rstrip("/")
                    probe = re.sub(r"<[^>]+>", "*", probe)
                    if not (list(root.glob(probe)) if "*" in probe else [1] if (root / probe).exists() else []):
                        bad.append(p)
                ok = not missing_skills and not bad
                print(f"  {'✓' if ok else '✗'} /{c:12} → {target:24} "
                      f"skills={len(set(SKILL_RE.findall(body)) & SKILLS)} paths={len(required)}"
                      + (f"  MISSING-SKILLS={missing_skills}" if missing_skills else "")
                      + (f"  MISSING-PATHS={bad}" if bad else ""))
                if not ok:
                    fails.append(f"{name}:/{c}")
    finally:
        if keep:
            print(f"\n(trees kept at {tmp})")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + ("✓ ALL SCENARIOS RUNNABLE" if not fails else f"✗ {len(fails)} FAILURE(S): {fails}"))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
