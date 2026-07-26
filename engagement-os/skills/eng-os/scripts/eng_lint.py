#!/usr/bin/env python3
"""Check an engagement repo against the invariants that are mechanically decidable.

These rules are enforced by prose everywhere else in the pack, which means they hold only as
well as whatever model happened to read that prose. Here they are checks — cheaper, deterministic,
and they don't get less reliable on a smaller model.

Judgment-bearing rules (did we miss a requirement? is this claim defensible? is the backbone the
right backbone?) are NOT here and can't be — those stay with a reviewer.

The section-file contract (status vocabulary, frontmatter fields, id syntax) lives in
references/section-contract.md with its machine form in section_contract.py — imported,
never re-declared here.

Usage:
    python3 eng_lint.py [repo-root] [--strict] [--list]

    --strict   treat warnings as failures too (use before shipping)
    --list     print the rule registry and exit (docs point here instead of enumerating)

Exit: 0 clean · 1 errors found · 2 repo doesn't look like an engagement repo
"""
import argparse
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import section_contract as sc

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


# ── shared helpers ─────────────────────────────────────────────────────────────

def resolve_in_repo(root, ref):
    """Does `ref` resolve to a real file? Root-relative first, then basename search.

    `archived/` and `.git/` are excluded: a reference that resolves ONLY into the
    archive points at a superseded file — the last thing a citation should hit.
    """
    if (root / ref).exists():
        return True
    name = os.path.basename(ref)
    for p in root.rglob(name):
        parts = set(p.relative_to(root).parts)
        if "archived" not in parts and ".git" not in parts:
            return True
    return False


def frozen_finals(root):
    """4_final directories that hold at least one real file (dotfiles don't count —
    a Finder .DS_Store must not flip a directory to 'frozen')."""
    out = []
    for d in root.rglob("4_final"):
        if d.is_dir() and any(f.is_file() and not f.name.startswith(".")
                              for f in d.rglob("*")):
            out.append(d)
    return out


def matrix_paths(root):
    return sorted(root.glob("01_pursuit/*/2_analysis/compliance_matrix.md"))


def matrix_req_ids(root):
    """Every R-nnn id present in any compliance matrix (None if there is no matrix)."""
    mats = matrix_paths(root)
    if not mats:
        return None
    ids = set()
    for m in mats:
        ids |= set(sc.REQ_ID_RE.findall(m.read_text(encoding="utf-8", errors="replace")))
    return ids


def firm_asset_ids(root):
    """Ids the firm-assets index actually holds (None if there is no index).

    The gaps section lists what we do NOT hold — ids harvested from the whole file
    counted a known-gap as held, so a matrix could cite the very asset we lack.
    """
    idx = root / "01_pursuit/_shared/firm_assets.md"
    if not idx.exists():
        return None
    text = idx.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"^#{1,3}\s+.*gap.*$", text, flags=re.M | re.I)
    return set(sc.ASSET_ID_RE.findall(parts[0]))


def matrix_table(root, m):
    """Parse a compliance matrix into (header-index map, [(lineno, cells)] real rows).

    Columns are located BY HEADER NAME, never by position — a reordered or extended
    matrix must not silently shift what 'status' means. A row is a template row when
    its id cell holds a placeholder (<...> or R-0xx); a literal '<' anywhere else in
    a real row ('limit < 10 pages') must not exempt the row.
    """
    lines = m.read_text(encoding="utf-8", errors="replace").splitlines()
    header, hmap, rows = None, {}, []
    for i, line in enumerate(lines, 1):
        raw = [c.strip() for c in line.split("|")]
        if header is None:
            lowered = [c.lower() for c in raw]
            if any("mandatory" in c or c in ("m / d", "m/d") for c in lowered) and \
               any("status" in c for c in lowered):
                header = i
                for n, c in enumerate(raw):
                    cl = c.lower()
                    if "mandatory" in cl or cl in ("m / d", "m/d"):
                        hmap["mandatory"] = n
                    elif "status" in cl:
                        hmap["status"] = n
                    elif re.fullmatch(r"(?:#|id|req(?:uirement)?\s*id?|ref)", cl):
                        hmap.setdefault("id", n)
                hmap.setdefault("id", 1)   # RFP matrices conventionally lead with the id
            continue
        if not sc.REQ_ID_RE.search(line):
            continue
        idcell = raw[hmap["id"]] if hmap["id"] < len(raw) else ""
        if "<" in idcell or re.fullmatch(r"R-0+x+", idcell.strip("`")):
            continue                                # planted template row
        rows.append((i, raw))
    return hmap, rows


# ── rules ────────────────────────────────────────────────────────────────────────

#: A leak cites a FILE inside the bucket; a guardrail only names the bucket. Requiring a
#: content directory + path segment after `engagement/` separates them, which matters because
#: the pack's own reuse-analysis template ends with "Nothing in `_sources/engagement/` is
#: [reusable]" — a prohibition the naive substring check reported as the very violation it
#: warns against. The `_sources/` prefix is optional: a relative `engagement/_md/…` mention
#: in a bid document is the same leak.
LEAK_RE = re.compile(r"(?:_sources/)?engagement/(?:_md|_raw|raw)/\S*[\w.-]")


def rule_bucket_leak(root, r):
    """engagement/ material must never be cited from a bid or pre-award research."""
    r.ran()
    for rel in ("01_pursuit", "00_research"):
        for p in text_files(root, rel):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if LEAK_RE.search(line):
                    r.error("bucket-leak", f"{p.relative_to(root)}:{i}",
                            "bid-side document cites engagement-bound material — "
                            "source it independently or drop the claim")


def rule_verify_not_shipped(root, r):
    """[⚠VERIFY] must not survive into a frozen/submitted or live-issued artefact."""
    r.ran()
    targets = [p for d in frozen_finals(root) for p in text_files(d)]
    targets += text_files(root, "00_research/2_output")
    for p in targets:
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if "⚠VERIFY" in line:
                r.error("verify-shipped", f"{p.relative_to(root)}:{i}",
                        "unverified claim in a shipped artefact — close it or cut it")


def rule_mandatory_met(root, r):
    """Every Mandatory compliance-matrix row must reach `met` before a response is frozen."""
    mats = matrix_paths(root)
    if not mats:
        return
    r.ran()
    for m in mats:
        frozen = bool(frozen_finals(m.parent.parent))
        hmap, rows = matrix_table(root, m)
        if not rows:
            # not-started is normal early (a fresh scaffold plants only the template
            # row) — but a frozen response over an empty matrix is a vacuous pass
            (r.error if frozen else r.warn)(
                "matrix-empty", str(m.relative_to(root)),
                "no real requirement rows — an empty matrix passes every check vacuously"
                + (" — and a response is already frozen" if frozen else ""))
            continue
        mi, si = hmap.get("mandatory", 4), hmap.get("status", 9)
        for i, cells in rows:
            mandatory = cells[mi] if mi < len(cells) else ""
            status = cells[si] if si < len(cells) else ""
            req = sc.REQ_ID_RE.search("|".join(cells))
            if mandatory.upper().startswith("M") and status.lower() != "met":
                where = f"{m.relative_to(root)}:{i}"
                msg = f"mandatory requirement {req.group(0) if req else '?'} is '{status}', not 'met'"
                (r.error if frozen else r.warn)("mandatory-open", where,
                                                msg + (" — and a response is already frozen" if frozen else ""))


def rule_citations_resolve(root, r):
    """Every `file.md §Page N` citation must point at a file that exists — outside the archive."""
    r.ran()
    pat = re.compile(r"`?([\w./-]+\.md)\s*§\s*(?:Page|Slide|Section|Sheet)\s*\S*")
    for rel in ("00_research", "02_delivery", "01_pursuit"):
        for p in text_files(root, rel):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for cited in pat.findall(line):
                    if "<" in cited:
                        continue          # template placeholder
                    if not resolve_in_repo(root, cited):
                        r.warn("dangling-citation", f"{p.relative_to(root)}:{i}",
                               f"cites '{cited}' — no such live file (archive doesn't count)")


def rule_findings_conform(root, r):
    """Every finding needs an evidence tag from the closed set and a backbone mapping."""
    fdir = root / "02_delivery/1_discovery/3_findings"
    if not fdir.exists():
        return
    r.ran()
    tag_re = re.compile(r"\[(Observed|Reported|Assumed|RFP)\]")
    findings = [p for p in fdir.rglob("*.md")
                if not p.name.startswith("_") and p.name != "README.md"]
    if not findings:
        r.warn("findings-empty", str(fdir.relative_to(root)),
               "no findings yet — the directory passing vacuously is not the same as conforming")
    dset = None
    dreg = root / "02_delivery/DELIVERABLES.md"
    if dreg.exists():
        dset = set(re.findall(r"\bD\d+\b", dreg.read_text(encoding="utf-8", errors="replace")))
    for p in findings:
        body = p.read_text(encoding="utf-8", errors="replace")
        # strip code spans first: quoting the standard's own tag list must not count as tagging
        prose = re.sub(r"`[^`]*`", "", body)
        if not tag_re.search(prose):
            r.error("finding-untagged", str(p.relative_to(root)),
                    f"no evidence tag — expected one of {' '.join(sorted(EVIDENCE_TAGS))}")
        feeds = re.search(r"^\s*(?:\*\*)?(?:Backbone|Maps to|Feeds)(?:\*\*)?\s*:(.*)$",
                          body, re.M | re.I)
        if not feeds:
            r.error("finding-unmapped", str(p.relative_to(root)),
                    "no Backbone:/Maps to:/Feeds: line — every finding maps to the backbone")
        elif dset is not None:
            for d in set(re.findall(r"\bD\d+\b", feeds.group(1))) - dset:
                r.warn("finding-feeds-unknown", str(p.relative_to(root)),
                       f"feeds {d}, which is not in the DELIVERABLES.md register")


def rule_live_index_resolves(root, r):
    """A live-file index must exist when its phase does, and must point at live files."""
    for idx in (root / "02_delivery/DELIVERABLES.md", root / "00_research/README.md"):
        if not idx.exists():
            if idx.parent.exists():
                r.warn("live-index-missing", str(idx.relative_to(root)),
                       "the phase directory exists but its live-file index does not — "
                       "nobody can tell which file is current")
            continue
        r.ran()
        for i, line in enumerate(idx.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for ref in re.findall(r"`([^`]+\.(?:pptx|xlsx|docx|pdf|md))`", line):
                if "<" in ref or "…" in ref:
                    continue          # template placeholder
                if not resolve_in_repo(root, ref):
                    r.warn("dangling-live-file", f"{idx.relative_to(root)}:{i}",
                           f"index points at '{ref}' which doesn't exist (archive doesn't count)")


def rule_spine_filled(root, r):
    """The spine must be real, not the planted placeholder — everything downstream depends on it.

    Only the spine SECTION is checked, not the whole file. Both index files carry other sections
    whose placeholders are legitimate and outlive the spine: the research README documents its
    citation format as `_sources/<bucket>/_md/<file>.md §Page N` and its versioning as
    `<CLIENT>_<ENG-ID>_...`, and the analysis/output tables stay templated until those artefacts
    exist. Scanning the whole file made the rule permanently red on a correctly-filled research
    repo — it fired on the instructions rather than on the spine.
    """
    checks = [
        (root / "02_delivery/1_discovery/3_findings/README.md", "findings backbone",
         r"^##\s+The backbone\b"),
        (root / "00_research/README.md", "research question list",
         r"^##\s+1\.\s+The questions\b"),
    ]
    for f, label, spine_head in checks:
        if not f.exists():
            continue
        r.ran()
        text = f.read_text(encoding="utf-8", errors="replace")
        # Narrow to the spine section when the planted heading is there; fall back to the whole
        # file when it isn't. Policing heading text is not this rule's job, and an adopted-in-place
        # repo is allowed its own wording — it just doesn't get the narrowing.
        spine = text
        start = re.search(spine_head, text, re.M)
        if start:
            rest = text[start.end():]
            end = re.search(r"^##\s", rest, re.M)
            spine = rest[:end.start()] if end else rest
        leftover = re.search(r"<[a-z][^>\n]{2,}>", spine)
        if leftover:
            r.warn("spine-unfilled", str(f.relative_to(root)),
                   f"{label} still holds a placeholder ({leftover.group(0)[:40]}…) — "
                   "sourced facts have nothing to map onto")


def rule_conditional_analysis_artefacts(root, r):
    """A worked analysis must have produced the artefacts it says it produced.

    Two artefacts in `2_analysis/` are conditional — `estimation.md` when the tender is priced,
    `bid_reuse_analysis.md` when a prior bid exists — and both failure modes cost real money.
    Found on the real GNI pursuit: a reuse analysis was generated with no check that a prior bid
    existed, and no estimate was produced at all, so the price had nothing behind it.

    The condition is read off `rfp_analysis.md` itself, which is why this can be mechanical: the
    template plants a pointer per artefact next to a placeholder. Placeholder still there → that
    section was never worked, nothing to check. Placeholder replaced → the analysis has committed
    to an answer, and the file it points at has to exist.
    """
    placeholder = re.compile(r"<[a-z€][^>\n]{2,}>", re.I)
    for f in sorted(root.glob("01_pursuit/*/2_analysis/rfp_analysis.md")):
        text = f.read_text(encoding="utf-8", errors="replace")
        for section, artefact, why in (
                (r"##\s*\d+\.\s*Estimate & price posture", "estimation.md",
                 "the price has nothing bottom-up behind it"),
                (r"##\s*\d+\.\s*Prior-bid reuse", "bid_reuse_analysis.md",
                 "the analysis says a prior bid carries over, but the diff was never done")):
            m = re.search(section + r"(.*?)(?=\n##\s|\Z)", text, re.S)
            if not m or placeholder.search(m.group(1)):
                continue                       # unworked section — not yet a claim
            r.ran()
            body = m.group(1)
            if re.search(r"not created|none found|no prior bid|n/?a\b", body, re.I):
                continue                       # the negative was recorded — that IS the result
            if not (f.parent / artefact).exists():
                r.error("analysis-artefact-missing", str(f.relative_to(root)),
                        f"§ points at `{artefact}`, which does not exist — {why}")


def rule_estimate_snapshot_fresh(root, r):
    """The generated markdown snapshot must not lag the workbook it was exported from.

    The workbook is the maintained artefact and the markdown is its export, which creates one
    failure mode the old two-file design did not have: edit the workbook, forget to re-export,
    and git now shows a snapshot that reads as current and is not. Everything downstream — lint,
    review, the diff someone uses to see what moved between two re-prices — is then reasoning
    from stale numbers that look authoritative.
    """
    for xlsx in sorted(root.glob("**/estimation.xlsx")):
        md = xlsx.with_suffix(".md")
        r.ran()
        if not md.exists():
            r.warn("estimate-snapshot-missing", str(xlsx.relative_to(root)),
                   "workbook has no markdown snapshot — run "
                   "`build_estimate_workbook.py --out <wb> --to-md`")
        elif xlsx.stat().st_mtime > md.stat().st_mtime + 1:
            r.warn("estimate-snapshot-stale", str(md.relative_to(root)),
                   "workbook is newer than its snapshot — re-export, or the diff everyone "
                   "reads is out of date")


PACK_ROOT_FILES = {"README.md", "00_REFERENCE_SUMMARY.md", "01_REFERENCE_INSIGHTS.md"}


def md_packs(root):
    """Every directory of converted markdown, with its content files.

    Two shapes, and both need policing. `_sources/<bucket>/_md/` groups by topic subfolder and
    keeps the summary/insights/README trio at its root. A tender pack's `1_received/_md/` has
    no topic grouping — the converted documents sit directly in it. Selecting content by
    "not in the pack root" is correct for the first shape and silently empties the second,
    which is how the most important document set in a bid escaped both rules.

    Yields (pack_dir, [content .md files]).
    """
    areas = list(root.glob("_sources/*/_md"))
    areas += list(root.glob("01_pursuit/*/1_received/_md"))
    for pack in areas:
        content = [p for p in pack.rglob("*.md") if p.name not in PACK_ROOT_FILES]
        yield pack, content


def rule_images_triaged(root, r):
    """Extracted images start tagged [uncertain]; leaving them there breaks the lossless rule.

    Found by running a real ingest: 52 images came out of four documents and nothing in the
    pack noticed that none of them had been triaged. This is the silent-decay case — the
    conversion "succeeded", so the gap never surfaces on its own. A second real run found the
    rule was only looking at `_sources/` — an untriaged figure in the RFP itself is worse,
    because scoring tables and requirement matrices arrive as images.
    """
    tag = re.compile(r"^\s*-\s*`?\[uncertain\]`?", re.I)
    for pack, content in md_packs(root):
        r.ran()
        for p in content:
            text = p.read_text(encoding="utf-8", errors="replace")
            n = sum(1 for line in text.splitlines() if tag.match(line))
            if n:
                r.warn("images-untriaged", str(p.relative_to(root)),
                       f"{n} extracted image(s) still `[uncertain]` — OCR them inline and retag "
                       "`[ocr-done]`, or classify as `[decorative]`/`[content]`")
            # A placed figure with no caption is only half-ingested: the pixels arrived, what
            # the document said they mean did not. The converter writes the stub; leaving it is
            # the same silent-decay failure as leaving an image untriaged.
            c = text.count("[caption-needed]")
            if c:
                r.warn("images-uncaptioned", str(p.relative_to(root)),
                       f"{c} placed figure(s) still `[caption-needed]` — write what each shows "
                       "in the words of the surrounding clause")


def rule_media_links_resolve(root, r):
    """Every image a converted MD links to must exist on disk.

    Found on the real GNI tender pack: pandoc emits raw HTML `<img src=...>` for any Word image
    that carries an explicit size, the converter only repointed the Markdown `![](…)` form, and
    every figure in every converted docx pointed into a deleted temp directory. Nothing noticed
    — the text conversion succeeded, and a dead image link renders as nothing at all. Same class
    as `rule_figures_exist`, one stage earlier in the pipeline.
    """
    ref_re = re.compile(r"!\[[^\]]*\]\(([^)]+)\)|<img\b[^>]*?src\s*=\s*[\"']([^\"']+)[\"']", re.I)
    for _pack, content in md_packs(root):
        for p in content:
            r.ran()
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                for m in ref_re.finditer(line):
                    ref = m.group(1) or m.group(2)
                    if not ref or ref.startswith(("http://", "https://", "data:")):
                        continue
                    if not (p.parent / ref).exists():
                        r.error("media-link-dead", f"{p.relative_to(root)}:{i}",
                                f"links '{ref}', which does not exist — the figure is lost and "
                                "the markdown gives no sign of it")


def rule_manifest_complete(root, r):
    """Every converted MD needs a manifest row, and every manifest row a file.

    The manifest is hand-maintained, so drift is invisible in BOTH directions: a missed row
    leaves a MD with no provenance, and a stale row points at a file that was renamed away.
    And a pack whose README is missing entirely must fail — 'no manifest' is the accident
    this rule exists to catch, not an exemption from it.
    """
    for pack, content in md_packs(root):
        readme = pack / "README.md"
        if not readme.exists():
            if content:
                r.error("manifest-absent", str(pack.relative_to(root)),
                        f"{len(content)} converted MD(s) and no README.md manifest — "
                        "their provenance isn't recorded anywhere")
            continue
        r.ran()
        listed = {os.path.basename(x) for x in re.findall(
            r"`([^`]+\.md)`", readme.read_text(encoding="utf-8", errors="replace"))}
        # [^`]+ not [\w./-]+ — real filenames have spaces ("26-002 - DataWarehouse ....md").
        # The [\w./-]+ version read zero rows from a manifest the converter had just written:
        # writer and reader each "worked", and together they reported every file as unlisted.
        present = {p.name for p in content}
        for p in content:
            if p.name not in listed:
                r.error("manifest-missing", str(p.relative_to(root)),
                        f"converted MD has no row in {readme.relative_to(root)} — "
                        "its provenance isn't recorded anywhere")
        for name in sorted(listed - present - {"README.md"}):
            if not (pack / name).exists():
                r.warn("manifest-stale-row", str(readme.relative_to(root)),
                       f"manifest row names '{name}', which no longer exists under the pack — "
                       "renamed or deleted without updating the manifest")


def rule_pointer_table_resolves(root, r):
    """CLAUDE.md's pointer table must point at files that exist.

    This is where an added block breaks things: the scaffolder won't touch an existing
    CLAUDE.md, so the rows for the new block are added by the agent — and a row naming a
    path that was never created sends every later lookup somewhere empty.
    """
    for name in ("CLAUDE.md", "AGENTS.md"):
        f = root / name
        if not f.exists():
            continue
        r.ran()
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not line.startswith("| ") or "`" not in line:
                continue
            for ref in re.findall(r"`([\w./_-]+\.(?:md|pptx|xlsx|docx|pdf))`", line):
                if "<" in ref:
                    continue
                if not (root / ref).exists():
                    r.error("pointer-dangling", f"{name}:{i}",
                            f"pointer table names '{ref}', which doesn't exist — "
                            "a block was probably added without topping up the table")


def rule_asset_refs_resolve(root, r):
    """Every `A-nnn` the matrix cites must exist in the firm-assets index.

    The Evidence column is where a bid quietly goes wrong: "case studies" reads as evidence but
    names nothing, and an id pointing at a row that was never written is worse — it looks checked.
    A matrix that cites assets while the index itself is missing is an error, not an exemption.
    """
    mats = matrix_paths(root)
    known = firm_asset_ids(root)
    if not mats:
        return
    r.ran()
    if known is None:
        for m in mats:
            if sc.ASSET_ID_RE.search(m.read_text(encoding="utf-8", errors="replace")):
                r.error("asset-index-missing", str(m.relative_to(root)),
                        "cites A-nnn assets but 01_pursuit/_shared/firm_assets.md does not exist")
        return
    for m in mats:
        for i, line in enumerate(m.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for ref in set(sc.ASSET_ID_RE.findall(line)) - known:
                r.error("asset-unknown", f"{m.relative_to(root)}:{i}",
                        f"cites {ref}, which has no row in firm_assets.md")


def section_files(root):
    base = root / "01_pursuit"
    if not base.exists():
        return []
    return sorted(base.glob("*/3_drafting/sections/*.md"))


def rule_section_frontmatter(root, r):
    """The frontmatter's load-bearing fields must reconcile with their registers.

    answers_reqs ↔ compliance matrix · evidence ↔ firm_assets.md · figures ↔ files on disk.
    A field that names an id nothing else knows is worse than an empty field — it reads as
    cross-checked. (Contract: references/section-contract.md.)
    """
    secs = section_files(root)
    if not secs:
        return
    r.ran()
    req_ids, asset_ids = matrix_req_ids(root), firm_asset_ids(root)
    for p in secs:
        meta, body = sc.parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        if not meta:
            continue                        # rule_section_budget already reports missing frontmatter
        where = str(p.relative_to(root))
        if req_ids is not None:
            for req in sorted(sc.fm_list(meta, "answers_reqs", sc.REQ_ID_RE) - req_ids):
                r.error("section-req-unknown", where,
                        f"answers_reqs names {req} — no such row in the compliance matrix")
        if asset_ids is not None:
            for a in sorted(sc.fm_list(meta, "evidence", sc.ASSET_ID_RE) - asset_ids):
                r.error("section-asset-unknown", where,
                        f"evidence names {a} — no such row in firm_assets.md")
        declared = sc.fm_list(meta, "figures", sc.FIG_ID_RE)
        fdir = p.parent.parent / "figures"
        on_disk = {m.group(1) for f in (fdir.glob("F-*") if fdir.exists() else [])
                   for m in [sc.FIG_FILE_RE.match(f.name)] if m}
        in_body = {m.group(1) for ref in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body)
                   for m in [sc.FIG_FILE_RE.match(os.path.basename(ref))] if m}
        for f in sorted(declared - on_disk):
            r.error("section-figure-unknown", where,
                    f"figures names {f} — no {f}_* file in {fdir.relative_to(root)}")
        for f in sorted(declared - in_body):
            r.warn("section-figure-unreferenced", where,
                   f"figures declares {f} but the body never references it")
        for f in sorted(in_body - declared):
            r.warn("section-figure-undeclared", where,
                   f"body references {f} but the frontmatter doesn't declare it")


def rule_section_budget(root, r):
    """Draft sections must declare a page budget and stay inside it.

    The page limit is the one format rule that changes what you write rather than how it looks,
    and it is checkable while drafting instead of after rendering — which is when a breach is
    expensive. At Arial 10, ~525 words fill one side of A4; a full-width figure costs ~half a page.
    """
    secs = section_files(root)
    if not secs:
        return
    r.ran()
    shared = {}
    for p in secs:
        meta, prose = sc.parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        if not meta:
            r.error("section-nofrontmatter", str(p.relative_to(root)),
                    "draft section has no frontmatter — marks, page budget and req mapping are unrecorded")
            continue
        if "page_budget" not in meta:
            r.warn("section-nobudget", str(p.relative_to(root)),
                   "no page_budget declared — the limit can't be tracked while drafting")
        prose = re.sub(r"^[>|].*$", "", prose, flags=re.M)          # our own notes + tables
        words = len(prose.split())
        figs = len(re.findall(r"^\s*!\[", prose, re.M))
        pages = words / 525 + figs * 0.5
        budget = meta.get("page_budget", "")
        m = re.search(r"(\d+)\s*A4", budget)
        if not m:
            continue
        limit = int(m.group(1))
        if "shared" in budget.lower():
            # A shared budget spans several files, so per-file checking always passes while the
            # group overruns. Pool on the NORMALIZED budget string — pooling on the raw string
            # let two spellings of the same pool each pass per-file (the original silent-pass,
            # one level down).
            shared.setdefault(sc.normalize_budget(budget), []).append((p, pages))
        elif pages > limit:
            r.error("section-overlength", str(p.relative_to(root)),
                    f"~{pages:.1f} A4 estimated against a stated limit of {limit} — "
                    "format non-compliance is a common auto-reject")

    for budget, members in shared.items():
        total = sum(pg for _p, pg in members)
        limit = int(re.search(r"(\d+)\s*a4", budget).group(1))
        if total > limit:
            r.error("section-overlength", ", ".join(str(f.name) for f, _ in members),
                    f"~{total:.1f} A4 across {len(members)} sections sharing a {limit}-page budget "
                    f'("{budget}") — the limit is on the group, not each file')


def rule_review_status(root, r):
    """A section's `status` must agree with its LATEST review verdict, and nothing unfinished
    may be frozen.

    Review rounds only work if their outcome is visible at a glance. The verdict column is
    located by header name (never position), and EVERY status is checked against the latest
    round — checking only the two extremes let `reviewed-r1` survive a later R2 'blocked'.
    """
    secs = section_files(root)
    if not secs:
        return
    r.ran()
    for p in secs:
        body = p.read_text(encoding="utf-8", errors="replace")
        where = str(p.relative_to(root))
        m = re.search(r"^status:\s*(\S+)", body, re.M)
        st = m.group(1) if m else None
        if st and st not in sc.ALL_STATUSES:
            r.warn("status-unknown", where,
                   f"status '{st}' is not one of {sorted(sc.ALL_STATUSES)}")

        # latest verdict from the review-log table, verdict column located by header
        verdicts = []   # (round, verdict)
        lines = body.splitlines()
        vcol = None
        for line in lines:
            cells = [c.strip() for c in line.split("|")]
            if vcol is None:
                lowered = [c.lower().strip("*") for c in cells]
                if "verdict" in lowered:
                    vcol = lowered.index("verdict")
                continue
            if len(cells) > vcol and re.fullmatch(r"R\d+", cells[1] if len(cells) > 1 else ""):
                v = cells[vcol].strip("*").lower()
                if v in sc.VERDICT_STATUS:
                    verdicts.append((cells[1], v))
        if st and verdicts:
            latest_round, latest = verdicts[-1]
            if st == "draft":
                r.warn("status-stale", where,
                       f"{latest_round} recorded '{latest}' but status is still 'draft'")
            elif st not in sc.VERDICT_STATUS[latest]:
                kind = (r.error if latest in ("revise", "blocked") and st == "approved"
                        else r.warn)
                kind("status-contradicts-review", where,
                     f"status '{st}' does not match the latest verdict "
                     f"({latest_round}: '{latest}')")
        elif st == "approved" and not verdicts:
            r.warn("status-unreviewed", where, "approved with no review-log verdicts")

    if frozen_finals(root / "01_pursuit"):
        unfinished = []
        for p in secs:
            m = re.search(r"^status:\s*approved\s*$",
                          p.read_text(encoding="utf-8", errors="replace"), re.M)
            if not m:       # no status line at all = never entered review = unfinished
                unfinished.append(str(p.name))
        if unfinished:
            r.error("frozen-unapproved", "01_pursuit/*/4_final/",
                    f"a response is frozen while {len(unfinished)} section(s) are not approved: "
                    + ", ".join(unfinished[:4]))


def rule_figures_exist(root, r):
    """Every image a draft section references must exist, and keep its editable source.

    Found by rendering for real: two sections cited figures that were never built, and the
    citation-resolution rule missed them because it only looks at `file.md §Page` references.
    Pandoc degrades a missing image to its alt text, so the document renders and the figure is
    simply gone — the failure is silent in exactly the place it costs most.
    """
    secs = section_files(root)
    if not secs:
        return
    r.ran()
    for p in secs:
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for ref in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", line):
                if "<" in ref or ref.startswith(("http://", "https://")):
                    continue                      # template placeholder / external
                target = (p.parent / ref).resolve()
                if not target.exists():
                    r.error("figure-missing", f"{p.relative_to(root)}:{i}",
                            f"references '{ref}', which does not exist — the render will silently "
                            "drop it to alt text")
                    continue
                for companion, why in ((".html", "editable source"), (".pptx", "editable one-slide export")):
                    if not target.with_suffix(companion).exists():
                        r.warn("figure-not-editable", str(p.relative_to(root)),
                               f"'{target.name}' has no {companion} {why} — a reviewer who cannot "
                               "edit sends the correction back as prose")


RULES = [rule_bucket_leak, rule_asset_refs_resolve, rule_section_frontmatter,
         rule_section_budget, rule_review_status, rule_figures_exist,
         rule_verify_not_shipped, rule_mandatory_met, rule_citations_resolve,
         rule_findings_conform, rule_live_index_resolves, rule_spine_filled,
         rule_conditional_analysis_artefacts, rule_estimate_snapshot_fresh,
         rule_images_triaged,
         rule_media_links_resolve, rule_manifest_complete, rule_pointer_table_resolves]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".", help="engagement repo root (default: cwd)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--list", action="store_true", help="print the rule registry and exit")
    args = ap.parse_args()

    if args.list:
        for rule in RULES:
            first = (rule.__doc__ or "").strip().splitlines()[0]
            print(f"  {rule.__name__}\t{first}")
        return 0

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
