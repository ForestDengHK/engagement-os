# Installing — and when to skip

Covers engagement-os and the plugins it delegates to. Three machine states, three
answers. Work out which one you are in first.

```
What is on this machine?
│
├─ nothing yet ............................. A. fresh machine → 3 marketplace adds + 1 install
├─ some of the plugins ..................... B. same command → it adds only what is missing
└─ everything, some as personal skills ..... C. nothing to install → eng-check companions
```

Not sure which? Ask the machine:

```
claude plugin list                     # what is installed as a plugin, and from which marketplace
/engagement-os:eng-check companions    # what resolves, how it is invoked here, what is missing
```

---

## A. Fresh machine — three adds, one install

The bundle's dependencies span three marketplaces, and Claude Code never adds a
marketplace for you — so all three adds come first:

```
/plugin marketplace add ForestDengHK/engagement-os
/plugin marketplace add ForestDengHK/panel-framework
/plugin marketplace add anthropics/skills
/plugin install consulting-suite@engagement-os
```

`consulting-suite` ships no components of its own; its manifest is a `dependencies`
list. Installing it resolves and installs `engagement-os`, `deck-craft` (figures and
decks), `panel-framework`, and `document-skills` (xlsx / docx / pptx / pdf):

```
✔ Successfully installed plugin: consulting-suite@engagement-os (scope: user)
  (+ 4 dependencies: engagement-os, deck-craft, panel-framework, document-skills)
```

**Want only engagement-os?** It declares no plugin dependencies, so this pulls in
exactly one plugin and never touches the rest of your setup:

```
/plugin install engagement-os@engagement-os
```

Either way, then install the Python parsers `convert_source.py` uses:

```
pip install pymupdf python-pptx python-docx openpyxl
# Homebrew / PEP-668 Python: add --user --break-system-packages, or use a venv
```

And, for document conversion and formula recalculation: `pandoc`, `markitdown`, and
LibreOffice (`soffice`). None of these are plugins, so no plugin command installs them.

## B. Some already installed — same command, it skips what you have

Run exactly the same four lines as A. Dependencies already installed **under the same
id** are skipped, and the install output names only what it actually added. Measured
2026-07-29 with `engagement-os@engagement-os` and `panel-framework@panel-framework`
already present:

```
$ claude plugin install consulting-suite@engagement-os
✔ Successfully installed plugin: consulting-suite@engagement-os (scope: user)
  (+ 2 dependencies: deck-craft, document-skills)
```

Skipping is automatic; there is no flag to pass and no flag needed.

## C. You already have everything — install nothing

If the skills are already on the machine — as plugins, or as personal skills in
`~/.claude/skills/` — there is nothing to do. Confirm with:

```
/engagement-os:eng-check companions
→ ✓ all 8 companions resolve — nothing to install.
```

The bundle is for machines that lack the plugins, not for machines that already work.

---

## What "already installed" actually means

The skip is keyed on the plugin id — `name@marketplace` — and nothing else.

| What you have | Does the bundle skip it? |
|---|---|
| Same plugin, same marketplace | **Yes.** Untouched. |
| Same plugin name, **different marketplace** | **No.** You get both. |
| The skill as a personal skill in `~/.claude/skills/` | **No.** A personal skill is not a plugin. |

The bundle lives in the **same** marketplace as `engagement-os` itself, so an existing
`engagement-os@engagement-os` is always recognized — the duplicate-copy trap only
appears if the same plugin name ever comes from two different marketplaces, which this
catalog never does.

### A personal skill is not a plugin

Skills in `~/.claude/skills/` load and work, but they are invisible to dependency
resolution and do not appear in `claude plugin list`. Install `deck-craft` while you
keep a personal `designing-figures` and you have both — they coexist rather than one
overriding the other, because a plugin skill is namespaced
(`deck-craft:designing-figures`) and a personal one is not. Keeping both is harmless;
if you want only the plugin copy, remove the personal one *after* installing.

This is also why the same skill answers to two different names depending on where it
came from. `eng-check companions` prints the name for the machine you are on:

```
  ✓ xlsx           xlsx                            ~/.claude/skills/xlsx
  ✓ panel-discuss  panel-framework:panel-discuss   ~/.claude/plugins/cache/panel-framework/...
```

---

## Updating

A plugin is cached under its manifest `version`, so **a release that does not bump
`version` never reaches anyone** — the cache key is unchanged and the update is a
no-op. If you publish here, bump `version` in `plugin.json` in the same commit as the
change.

To pull an update, refresh the marketplace first, then update by **full id**; `claude
plugin update <name>` without the marketplace suffix reports `Plugin not found`:

```
claude plugin marketplace update engagement-os
claude plugin update engagement-os@engagement-os
```

Then `/reload-plugins`, or restart — an updated plugin's skills are not live in a
session that was started before the update.

Auto-update is off by default for non-Anthropic marketplaces; turn it on per
marketplace in `/plugin` if you would rather not do this by hand.

## Uninstalling

```
claude plugin uninstall consulting-suite@engagement-os --prune
```

`--prune` also removes dependencies that were auto-installed and are no longer
required by anything. Plugins you installed yourself are never pruned. `claude plugin
prune --dry-run` lists what would go without removing it.

## Verifying an install

```
/engagement-os:eng-check companions
```

Reports every delegated-to skill, where it resolved from, how to invoke it here, and —
only if something is genuinely absent — the exact install commands. Exit 0 means there
is nothing to do.
