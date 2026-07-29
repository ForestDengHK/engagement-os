# Engagement OS

A composable operating system for document-heavy consulting engagements — research, bid,
delivery, or all three — as a Claude Code plugin marketplace.

**Installing? Read the guide: [`engagement-os/INSTALL.md`](engagement-os/INSTALL.md)** —
three machine states (fresh / partial / already-have-everything), what to run for each, and
when the answer is "install nothing".

## What's in this repo

This repo is one marketplace (`engagement-os`) hosting three plugins:

| Plugin | What it is |
|---|---|
| [`engagement-os/`](engagement-os/) | The pack itself: 16 `eng-*` skills covering pursuit (rfp-analyze → bid-research → bid-respond) and delivery (ingest → findings → deliverable), with mechanical gates, templates and scripts. Declares **no plugin dependencies** — installing it alone pulls nothing else. |
| [`deck-craft/`](deck-craft/) | Client-grade deck and figure craft: `presentation-builder` + `designing-figures`. The render end of engagement-os, or standalone. |
| [`consulting-suite/`](consulting-suite/) | Install-everything bundle for a fresh machine — a manifest-only plugin whose dependency list resolves engagement-os + deck-craft + panel-framework + the Office document skills, skipping anything already installed. Manifest-only by design: the directory holds just `.claude-plugin/plugin.json`. |

## Quick start

**Fresh machine** (one command installs all four plugins):

```
/plugin marketplace add ForestDengHK/engagement-os
/plugin marketplace add ForestDengHK/panel-framework
/plugin marketplace add anthropics/skills
/plugin install consulting-suite@engagement-os
```

**Core only** (pulls exactly one plugin):

```
/plugin marketplace add ForestDengHK/engagement-os
/plugin install engagement-os@engagement-os
```

**Already have everything** (old machine): don't install anything — update and verify:

```
claude plugin marketplace update engagement-os
claude plugin update engagement-os@engagement-os
/engagement-os:eng-check companions
```

Docs: [`engagement-os/README.md`](engagement-os/README.md) ·
[`engagement-os/INSTALL.md`](engagement-os/INSTALL.md) ·
[`engagement-os/USAGE.md`](engagement-os/USAGE.md)
