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

# scenario -> (mode, [commands], [content assertions])
# Asserted below against USAGE.md: every numbered scenario there is tested here; tested
# scenarios beyond the numbered list are standalone stages (6 render, 7 variant).
SCENARIOS = {
    "1 research only": ("research", ["eng-new", "eng-source", "eng-sprint"], []),
    "2 pursuit only": ("pursuit", ["eng-new", "eng-rfp"], []),
    "3 delivery only": ("delivery", ["eng-new", "eng-source", "eng-workshop", "eng-sprint"], []),
    "4 bid then deliver": ("full", ["eng-new", "eng-rfp", "eng-source", "eng-workshop", "eng-sprint"], []),
    "5 upgrade (pursuit +delivery)": ("pursuit->pursuit,delivery", ["eng-upgrade"], []),
    "6 render (standalone)": ("pursuit", ["eng-render"], []),
    "7 pursuit mini-comp (variant)": ("pursuit|mini-comp", ["eng-rfp"], [
        ("01_pursuit/27-010/2_analysis/rfp_analysis.md", "mini-comp"),
    ]),
}

PATH_RE = re.compile(r"`((?:_sources|_pm|00_research|01_pursuit|02_delivery)/[\w<>./-]*)`")
SKILL_RE = re.compile(r"`(eng-[a-z-]+)`")

# A typo'd top-level path (`01_pursit/…`) never matches PATH_RE, so it was never
# required to exist — a silent pass. Top-level-looking means: numbered (`NN_foo`)
# or underscore-led (`_foo`); relative fragments (engagement/, 4_final/) don't match.
TOPLIKE_RE = re.compile(r"`((?:\d{2}_[\w-]+|_[a-z][\w-]*)/[\w<>./-]*)`")
KNOWN_TOP = {"00_research", "01_pursuit", "02_delivery", "_sources", "_pm"}

LINT = ROOT / "skills/eng-os/scripts/eng_lint.py"
USAGE = ROOT / "USAGE.md"


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
    variant = "full-rfp"
    if "|" in mode:
        mode, variant = mode.split("|", 1)          # "pursuit|mini-comp"
    steps = mode.split("->")  # "a->b" = scaffold a, then additively scaffold b
    for step in steps:
        subprocess.run(
            [sys.executable, str(SCAFFOLD), "--root", str(root), "--client", "ACME",
             "--eng-id", "27-010", "--name", "Study", "--mode", step,
             "--variant", variant],
            check=True, capture_output=True)
    return blocks_of(steps[-1])


def usage_scenario_numbers():
    """Scenario numbers documented in USAGE.md (## Scenario N — …). The standalone
    render stage is documented as a stage, not a numbered scenario, so it is
    accounted for separately below."""
    if not USAGE.exists():
        return None
    return {int(n) for n in re.findall(r"^## Scenario (\d+)", USAGE.read_text(), re.M)}


def main():
    keep = "--keep" in sys.argv
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="engos-e2e-"))
    fails = []

    documented = usage_scenario_numbers()
    tested = {int(k.split()[0]) for k in SCENARIOS}
    if documented is not None:
        # every numbered scenario in USAGE.md is tested; the only tested scenarios
        # allowed beyond the numbered list are the standalone stages (render, variant)
        missing = documented - tested
        extra = tested - documented - {6, 7}
        if missing or extra:
            fails.append("SCENARIOS↔USAGE.md")
            print(f"✗ scenario mirror: documented-not-tested={sorted(missing)} "
                  f"tested-not-documented={sorted(extra)}")
    try:
        for name, (mode, cmds, assertions) in SCENARIOS.items():
            root = tmp / re.sub(r"[^a-z]+", "_", name)
            blocks = scaffold(root, mode)
            print(f"\n─── {name}   mode={mode}   blocks={sorted(blocks)} ───")

            for rel, needle in assertions:
                f = root / rel
                ok = f.exists() and needle in f.read_text()
                print(f"  {'✓' if ok else '✗'} planted: {rel} contains {needle!r}")
                if not ok:
                    fails.append(f"{name}:planted:{rel}")

            # a freshly scaffolded tree must lint with ZERO errors — if a planted
            # template trips an error, every new engagement starts with a red gate
            # and users learn to ignore the gate (worse than no gate)
            lint = subprocess.run([sys.executable, str(LINT), str(root)],
                                  capture_output=True, text=True)
            n_err = lint.stdout.count("ERROR [")
            print(f"  {'✓' if n_err == 0 else '✗'} fresh tree lints with {n_err} error(s)")
            if n_err:
                fails.append(f"{name}:fresh-lint")
                for line in lint.stdout.splitlines():
                    if "ERROR [" in line:
                        print(f"      {line.strip()}")

            for c in cmds:
                f = CMD / f"{c}.md"
                if not f.exists():
                    print(f"  ✗ /{c}: command file missing"); fails.append(f"{name}:/{c}"); continue
                text = f.read_text()
                # A command may name one or several targets (playbooks and/or skills).
                # EVERY named target must resolve — checking only the first let a
                # rotten second reference go silent.
                bodies, unresolved = [], []
                for pb in re.findall(r"playbooks/([\w-]+\.md)", text):
                    if (PB / pb).exists():
                        bodies.append((PB / pb).read_text())
                    else:
                        unresolved.append(f"playbooks/{pb}")
                for sk in re.findall(r"skills/(eng-[\w-]+)/SKILL\.md", text):
                    if (ROOT / "skills" / sk / "SKILL.md").exists():
                        bodies.append((ROOT / "skills" / sk / "SKILL.md").read_text())
                    else:
                        unresolved.append(f"skills/{sk}/SKILL.md")
                if not bodies and not unresolved:
                    print(f"  ✗ /{c}: neither a playbook nor a skill target resolves")
                    fails.append(f"{name}:/{c}"); continue
                if unresolved:
                    print(f"  ✗ /{c}: unresolved target(s) {unresolved}")
                    fails.append(f"{name}:/{c}"); continue
                target = " + ".join(sorted(set(re.findall(r"playbooks/([\w-]+\.md)", text)
                                                + re.findall(r"skills/(eng-[\w-]+)", text))))
                body = "\n".join(bodies)

                typo = sorted({p for p in TOPLIKE_RE.findall(body)
                               if p.split("/")[0] not in KNOWN_TOP})
                missing_skills = sorted(set(SKILL_RE.findall(body)) - SKILLS)
                required = {p for p in PATH_RE.findall(body) if owned_by_selected(p, blocks)}
                bad = []
                for p in sorted(required):
                    # <ENG-ID> is concrete; any other <placeholder> is a naming pattern → glob it.
                    probe = p.replace("<ENG-ID>", "27-010").rstrip("/")
                    probe = re.sub(r"<[^>]+>", "*", probe)
                    if not (list(root.glob(probe)) if "*" in probe else [1] if (root / probe).exists() else []):
                        bad.append(p)
                ok = not missing_skills and not bad and not typo
                print(f"  {'✓' if ok else '✗'} /{c:12} → {target:24} "
                      f"skills={len(set(SKILL_RE.findall(body)) & SKILLS)} paths={len(required)}"
                      + (f"  MISSING-SKILLS={missing_skills}" if missing_skills else "")
                      + (f"  MISSING-PATHS={bad}" if bad else "")
                      + (f"  UNKNOWN-TOP-PATHS={typo}" if typo else ""))
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
