# Scenario — native figures in a deck

**Skills under test:** `eng-render` (deck route) → `presentation-builder` → `designing-figures`.

## RED (baseline, observed 2026-10-07)

A 47-slide bid deck shipped seven figures as PNG renders of HTML. Bid lead: "slide uses image
and can't editable." The `.pptx` sibling the section contract then asked for was produced by no step;
`designing-figures` ended at PNG. `verify_deck.py` passed the deck: `flattened-slide` only fires
on a full-bleed picture with no text, and every figure slide had a title.

## Task given to the agent

> Build a 2-slide deck with one swimlane figure from this spec. Slide 1: title slide. Slide 2:
> the figure.

```
Action title:  Every change reaches the client in five hand-offs
Destination:   deck
Archetype:     swimlane
Lanes:         Client · Delivery team · Platform
Steps:         Raise request (Client) → Triage & size (Delivery) → Build change (Delivery)
               → Deploy (Platform) → Accept (Client)
```

## Pass (GREEN)

| Check | Command | Expected |
|---|---|---|
| no pictures on slide layers | `for f in $(unzip -Z1 deck.pptx 'ppt/slides/slide*.xml'); do unzip -p deck.pptx "$f" \| grep -c '<p:pic>'; done` | `0` for every slide |
| figure is editable | python-pptx: slide 2 has a group shape; its children are autoshapes + connectors; every step label is a text run | 5 step labels + 3 lane headers as text runs |
| connectors glued | each connector's `<a:stCxn>` / `<a:endCxn>` names a step shape | 4 connectors, all glued |
| package gate | `verify_deck.py --figures native deck.pptx --expect 2` | `✓ clean`, no `font-not-embedded`, no `picture-on-slide` |
| type minimums | title 20–24 pt, labels ≥ 12 pt | met |

Fail signals: any `<p:pic>` on slide 2; the agent renders HTML → PNG first "to be safe"; the
figure as loose ungrouped shapes; `font.name` hard-set to a non-theme font.

## Evidence (2026-10-08)

The worked example in `designing-figures` `references/render-pipeline.md` §7, extracted and run
as-is: 0 `<p:pic>`; group of 15 shapes (6 lane bands/headers, 5 steps, 4 glued connectors — 8
carrying text); `verify_deck.py --expect 1` → `✓ clean`; LibreOffice round-trip render reads
correctly. Control: the same deck with one 40×40 PNG added to slide 2 still passes
`verify_deck.py` (`✓ clean`) and the picture-count loop in eng-os `deck-assembly.md` reports
`slide2.xml: 1 picture(s)` — the loop, not `verify_deck.py`, is what catches a pasted figure.
Since then `verify_deck.py` lists every slide picture itself (`picture-on-slide`: a warning,
an error under `--figures native`), so the gate row above catches the control too.
