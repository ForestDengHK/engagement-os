# Installing — and when to skip

Covers engagement-os and the skills it delegates to. Three machine states, three answers.
Work out which one you are in first; the wrong path does not fail loudly, it silently gives
you two copies of everything.

```
Do you already have these as CLAUDE CODE PLUGINS?
│
├─ nothing installed ......................... A. fresh machine → install the bundle
├─ some plugins from the same catalog ........ B. partial → install the bundle, it adds only what's missing
├─ plugins from a DIFFERENT marketplace ...... C. do NOT install the bundle → see "Same name, different id"
└─ they're personal skills in ~/.claude/skills  D. do NOT install the bundle → see "A personal skill is not a plugin"
```

Not sure which? Ask the machine:

```
claude plugin list                     # what is installed as a plugin, and from which marketplace
/engagement-os:eng-check companions    # what resolves, how it is invoked here, what is missing
```

---

## A. Fresh machine — one command

```
/plugin marketplace add ForestDengHK/forest-consulting
/plugin install consulting-suite@forest-consulting
```

`consulting-suite` ships no components of its own; its manifest is a `dependencies` list.
Installing it resolves and installs `engagement-os`, `panel-framework`, `deck-craft`
(figures and decks), and `document-skills` (xlsx / docx / pptx / pdf).

**Want only engagement-os?** It declares no plugin dependencies, so this pulls in exactly
one plugin and never touches the rest of your setup:

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

## B. Partial — the same command, it skips what you have

Run exactly the same two lines as A. Already-installed dependencies are skipped, and the
install output names only what it actually added:

```
$ claude plugin install consulting-suite@<catalog>
✔ Successfully installed plugin: consulting-suite (scope: user) (+ 2 dependencies: engagement-os, deck-craft)
```

With **all** dependencies already installed, the same command reports no dependency line at
all — nothing was reinstalled:

```
$ claude plugin install consulting-suite@<catalog>
✔ Successfully installed plugin: consulting-suite (scope: user)
```

Both measured against a local copy of the catalog, 2026-07-29. Skipping is automatic; there
is no flag to pass and no flag needed.

## C / D. You already have everything — skip the install entirely

Then do nothing. `consulting-suite` would not save you a step; it would cost you duplicates.
Confirm with:

```
/engagement-os:eng-check companions
→ ✓ all 8 companions resolve — nothing to install.
  Skip the install step; `consulting-suite` would add nothing here.
```

---

## What "already installed" actually means

The skip is keyed on the plugin id — `name@marketplace` — and nothing else.

| What you have | Does the bundle skip it? |
|---|---|
| Same plugin, same marketplace | **Yes.** Untouched. |
| Same plugin name, **different marketplace** | **No.** You get both. |
| The skill as a personal skill in `~/.claude/skills/` | **No.** A personal skill is not a plugin. |

### Same name, different id

If `engagement-os` came from the standalone `ForestDengHK/engagement-os` marketplace, the
bundle's dependency resolves to `engagement-os@forest-consulting` — a different id — and
installs a second copy:

```
$ claude plugin install consulting-suite@<catalog>
✔ ... (+ 3 dependencies: engagement-os, panel-framework, deck-craft)

  ❯ engagement-os@engagement-os      ← the one you had
  ❯ engagement-os@<catalog>          ← the bundle installed another
```

Pick one catalog. If you are moving to the bundle, uninstall the old plugin and remove the
old marketplace *before* installing it:

```
claude plugin uninstall engagement-os@engagement-os
claude plugin marketplace remove engagement-os
```

### A personal skill is not a plugin

Skills in `~/.claude/skills/` load and work, but they are invisible to dependency resolution
and do not appear in `claude plugin list`. Install `deck-craft` while you keep a personal
`designing-figures` and you have both — they coexist rather than one overriding the other,
because a plugin skill is namespaced (`deck-craft:designing-figures`) and a personal one is
not. Remove the personal copy *after* installing, or don't install that plugin.

This is also why the same skill answers to two different names depending on where it came
from. `eng-check companions` prints the name for the machine you are on:

```
  ✓ xlsx           xlsx                            ~/.claude/skills/xlsx
  ✓ panel-discuss  panel-framework:panel-discuss   ~/.claude/plugins/cache/panel-framework/...
```

---

## Updating

A plugin is cached under its manifest `version`, so **a release that does not bump `version`
never reaches anyone** — the cache key is unchanged and the update is a no-op. If you publish
here, bump `version` in `plugin.json` in the same commit as the change.

To pull an update, refresh the marketplace first, then update by **full id**; `claude plugin
update <name>` without the marketplace suffix reports `Plugin not found`:

```
claude plugin marketplace update engagement-os
claude plugin update engagement-os@engagement-os
```

Then `/reload-plugins`, or restart — an updated plugin's skills are not live in a session
that was started before the update.

Auto-update is off by default for non-Anthropic marketplaces; turn it on per marketplace in
`/plugin` if you would rather not do this by hand.

## Uninstalling

```
claude plugin uninstall consulting-suite@forest-consulting --prune
```

`--prune` also removes dependencies that were auto-installed and are no longer required by
anything. Plugins you installed yourself are never pruned. `claude plugin prune --dry-run`
lists what would go without removing it.

## Verifying an install

```
/engagement-os:eng-check companions
```

Reports every delegated-to skill, where it resolved from, how to invoke it here, and — only
if something is genuinely absent — the exact install commands. Exit 0 means there is nothing
to do.
