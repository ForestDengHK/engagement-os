#!/usr/bin/env python3
"""Regression tests for scaffold_engagement.py — the planted .gitignore, the auto-memory directory
slug, CLAUDE.md with no empty headers, and an engagement log brief-me can actually read.

HOME is redirected to a temp dir for every scaffold run: the scaffolder writes the auto-memory
index under ~/.claude/projects/, and a test must never touch the real one.
"""
import datetime
import importlib.util
import os
import pathlib
import re
import subprocess
import sys

import pytest

PLUGIN = pathlib.Path(__file__).resolve().parents[1]
SCAFFOLD = PLUGIN / "skills/eng-os/scripts/scaffold_engagement.py"
GATHER = pathlib.Path.home() / ".claude/skills/brief-me/scripts/gather.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


se = load("scaffold_engagement", SCAFFOLD)


def scaffold(root, home, mode="pursuit"):
    r = subprocess.run([sys.executable, str(SCAFFOLD), "--root", str(root), "--client", "ACME",
                        "--eng-id", "27-010", "--name", "Data Platform Assessment",
                        "--mode", mode],
                       capture_output=True, text=True, env=dict(os.environ, HOME=str(home)))
    assert r.returncode == 0, r.stdout + r.stderr
    return r


# ── C2. memory directory slug ─────────────────────────────────────────────────

def test_memory_slug_matches_the_harness():
    assert se.memory_slug("/Users/party/projects/acme_it_ps") == "-Users-party-projects-acme-it-ps"


def test_memory_slug_replaces_dots_and_every_non_alphanumeric():
    assert se.memory_slug("/Users/a.b/my.proj v2+x") == "-Users-a-b-my-proj-v2-x"


def test_scaffold_writes_memory_into_the_harness_directory(tmp_path):
    root = tmp_path / "acme_27.010"
    scaffold(root, tmp_path / "home")
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(root))
    assert (tmp_path / "home/.claude/projects" / slug / "memory/MEMORY.md").exists()


# ── C1. .gitignore ────────────────────────────────────────────────────────────

def git_ignored(root, rel):
    return subprocess.run(["git", "-C", str(root), "check-ignore", "-q", rel]).returncode == 0


def test_gitignore_keeps_binaries_out_and_markdown_in(tmp_path):
    root = tmp_path / "eng"
    scaffold(root, tmp_path / "home")
    text = (root / ".gitignore").read_text(encoding="utf-8")
    for ext in ("pptx", "docx", "pdf", "xlsx", "xlsm", "png", "jpg"):
        assert f"01_pursuit/_shared/**/*.{ext}" in text
    for ext in ("pdf", "docx", "pptx", "xlsx"):
        assert f"_sources/**/*.{ext}" in text
    assert "!01_pursuit/_shared/_md/**" in text
    assert "**/_render/slides_png*/" in text and "**/__pycache__/" in text
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for rel in ("01_pursuit/_shared/case_studies/Big Deck.pptx",
                "01_pursuit/_shared/finance/rates.xlsm",
                "_sources/pre_award/RFT.pdf",
                "01_pursuit/27-010/3_drafting/_render/slides_png_v3/s01.png",
                "skills/__pycache__/x.pyc"):
        assert git_ignored(root, rel), rel
    for rel in ("01_pursuit/_shared/_md/case_studies/Big Deck.md",
                "01_pursuit/_shared/_md/images/fig1.png",
                "_sources/pre_award/_md/RFT.md",
                "_sources/pre_award/_md/images/p3.png",
                "01_pursuit/_shared/firm_assets.md"):
        assert not git_ignored(root, rel), rel


def test_gitignore_appends_to_an_existing_file_once(tmp_path):
    root = tmp_path / "eng"
    root.mkdir()
    (root / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    scaffold(root, tmp_path / "home")
    scaffold(root, tmp_path / "home")                       # re-run: additive, no duplicates
    text = (root / ".gitignore").read_text(encoding="utf-8")
    assert text.startswith("node_modules/\n")
    assert text.count("!01_pursuit/_shared/_md/**") == 1


# ── C3. CLAUDE.md has no empty headers ───────────────────────────────────────

def section_bodies(md):
    out, cur = {}, None
    for line in md.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return out


@pytest.mark.parametrize("mode", ["pursuit", "research", "full"])
def test_claude_md_has_no_empty_headers(tmp_path, mode):
    root = tmp_path / "eng"
    scaffold(root, tmp_path / "home", mode)
    md = (root / "CLAUDE.md").read_text(encoding="utf-8")
    md_no_comments = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    empty = [h for h, body in section_bodies(md_no_comments).items()
             if not any(ln.strip() for ln in body)]
    assert empty == []
    bodies = section_bodies(md_no_comments)
    contacts = "\n".join(bodies["Key Contacts"])
    assert ".claude/project-context.md" in contacts and "Stakeholder Map" in contacts
    panel = "\n".join(bodies["Panel Framework (if used)"])
    assert ".claude/panel-config.yaml" in panel and "/panel-init" in panel


# ── C4. engagement log lines brief-me reads ──────────────────────────────────

def test_engagement_log_template_carries_deadline_and_open_lines(tmp_path):
    root = tmp_path / "eng"
    scaffold(root, tmp_path / "home")
    log = (root / "_pm/engagement_log.md").read_text(encoding="utf-8")
    assert re.search(r"^- Deadline: YYYY-MM-DD — <what>$", log, re.M)
    assert re.search(r"^- Open: <who> · <what> · since YYYY-MM-DD$", log, re.M)


@pytest.mark.skipif(not GATHER.exists(), reason="brief-me not installed")
def test_brief_me_reads_a_filled_entry_and_the_claude_md_deadline(tmp_path):
    gather = load("gather", GATHER)
    root = tmp_path / "eng"
    scaffold(root, tmp_path / "home")
    today = datetime.date.today()
    due = (today + datetime.timedelta(days=2)).isoformat()
    since = today.isoformat()
    # a fresh scaffold must not report placeholder threads or deadlines
    paths = [p for p in gather.files(root)]
    assert gather.open_threads(paths, root)[0] == []
    assert gather.deadlines(paths, root, today) == []
    # an agent fills the entry template exactly as written
    log_path = root / "_pm/engagement_log.md"
    log = log_path.read_text(encoding="utf-8")
    entry = re.search(r"```markdown\n(.*?)```", log, re.S).group(1)
    filled = (entry.replace("YYYY-MM-DD — <session / event>", f"{since} — Kick-off")
                   .replace("Deadline: YYYY-MM-DD — <what>", f"Deadline: {due} — submission")
                   .replace("Open: <who> · <what> · since YYYY-MM-DD",
                            f"Open: Alex · pricing sign-off · since {since}"))
    log_path.write_text(log.replace("---\n\n", "---\n\n" + filled + "\n", 1), encoding="utf-8")
    claude = root / "CLAUDE.md"
    claude.write_text(claude.read_text(encoding="utf-8").replace(
        "**Next deadline:** YYYY-MM-DD — <what>", f"**Next deadline:** {due} — submission"),
        encoding="utf-8")
    paths = [p for p in gather.files(root)]
    threads = [t["text"] for t in gather.open_threads(paths, root)[0]]
    assert f"Open: Alex · pricing sign-off · since {since}" in threads
    assert f"Deadline: {due} — submission" in threads
    assert [d["date"] for d in gather.deadlines(paths, root, today)] == [due]
