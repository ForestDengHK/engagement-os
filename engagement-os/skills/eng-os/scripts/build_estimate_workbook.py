#!/usr/bin/env python3
"""Turn an estimate into a formula-live Excel workbook — the model, not a picture of one.

An estimate is a spreadsheet wearing prose. In markdown, changing one line item from 20 days to
26 means recomputing the total, the PERT mean, sigma, P50, P80, contingency, labour cost, the
cost base at two confidence levels, four margin figures and twelve mark scores — by hand, in a
document nobody can recalculate. That is how the arithmetic slips that this pack has already
caught twice get in, and it is why a reviewer cannot do the one thing a reviewer most wants to
do: change an input and see what happens.

So the workbook carries **formulas, not values**. Every derived cell is a real Excel formula over
input cells, and the input cells are the ones a reviewer is invited to move: rates, day counts,
the correlation assumption, the assumed competitor range. Nothing downstream has to be re-entered.

    markdown  = the narrative — assumptions, the overlap audit's reasoning, the decision framing
    workbook  = the model     — the numbers, live, editable, self-recalculating

The markdown seeds the workbook (this script reads its tables); after that the workbook is the
working artefact and the markdown quotes it. `--check` re-runs the arithmetic in Python and
reports where the markdown's own stated numbers disagree with its own inputs.

Usage:
    python3 build_estimate_workbook.py <estimation.md> [--out <file.xlsx>] [--rho 0.5]
    python3 build_estimate_workbook.py --blank --out estimation.xlsx    # starter, no markdown yet
    python3 build_estimate_workbook.py <estimation.md> --check          # arithmetic audit only

Requires openpyxl (pip install openpyxl).
"""
from __future__ import annotations

import argparse
import math
import os
import pathlib
import re
import sys

# Conventions are NOT invented here. They are the `xlsx` skill's financial-model conventions,
# which is the firm-wide standard every other spreadsheet already follows: blue text for
# hardcoded inputs, black for formulas, green for cross-sheet links, yellow fill for cells the
# reader is meant to edit, Arial throughout. A model that colour-codes itself differently from
# every other model in the building teaches the reader nothing and costs them a legend.
FONT = "Arial"
BLUE = "0000FF"            # hardcoded input / scenario lever
BLACK = "000000"           # formula
GREEN = "008000"           # formula referencing another sheet
YELLOW = "FFFF00"          # fill: edit this cell
HEAD_FILL = "1F3864"
EUR = '€#,##0'
PCT = '0.0%'               # stored as a fraction, per the xlsx skill
MULT = '0.0"x"'
# Legacy aliases so the per-cell calls below stay readable; `enforce_conventions` is what
# actually decides colour, from what each cell IS rather than from where it was written.
INPUT_FILL = YELLOW
DERIVED_FILL = "FFFFFF"


def _cells(line):
    """Split a markdown table row into stripped cells."""
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _num(s):
    """A number out of a markdown cell, or None. Tolerates €, commas, bold, footnotes."""
    if s is None:
        return None
    s = re.sub(r"[*`€£$,\s]|\(.*?\)", "", str(s))
    s = s.replace("−", "-").replace("–", "-")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else None


TABLE_KINDS = ("effort", "overlap", "grades", "ratecard", "client", "scope", "certain")
_MARKER = re.compile(r"^\s*<!--\s*table:(\w+)\s*-->\s*$")


def parse_tables(md):
    """Pull the model-bearing tables out of the estimation markdown, located by explicit markers.

    Each machine-read table is preceded by `<!--table:effort-->` and friends, planted by the
    template. The first version sniffed header text instead, and on the real GNI estimate it
    matched the §1 assumptions table as if it were the client-effort table — pulling "S-10, S-13
    (42 d)" out as `-10 sessions`. Nothing crashed; the client-hours total was simply wrong by a
    factor of seven. Guessing which table is which from its wording is not robust to an author
    rewording a heading, and the failure is silent, which is the worst combination.

    A marker with no table, or a table with no marker, yields nothing for that kind and is
    reported by the caller — never a silent zero, which reads like a real answer.
    """
    lines = md.splitlines()
    found = {k: [] for k in TABLE_KINDS}

    def rows_after(i):
        """Rows of the first markdown table starting at or after line i (skipping its header
        and the |---| separator). Stops at the first non-table line."""
        j = i
        while j < len(lines) and not lines[j].strip().startswith("|"):
            if lines[j].strip() and not _MARKER.match(lines[j]):
                return []                               # something other than blank intervened
            j += 1
        out = []
        for line in lines[j + 2:]:
            if not line.strip().startswith("|"):
                break
            out.append(_cells(line))
        return out

    def clean(s):
        return re.sub(r"[*`]", "", s).strip()

    for i, line in enumerate(lines):
        m = _MARKER.match(line)
        if not m or m.group(1) not in TABLE_KINDS:
            continue
        kind, rows = m.group(1), rows_after(i + 1)
        for r in rows:
            if kind == "effort" and len(r) >= 6:
                sid, o, mm, p = clean(r[0]), _num(r[3]), _num(r[4]), _num(r[5])
                if re.match(r"^S-\d+$", sid) and None not in (o, mm, p):
                    found["effort"].append((sid, clean(r[1]), o, mm, p,
                                            clean(r[-1]) if len(r) > 7 else ""))
            elif kind == "overlap" and len(r) >= 3:
                item, a, b = clean(r[0]), _num(r[1]), _num(r[2])
                if item and not item.upper().startswith("TOTAL") and None not in (a, b):
                    found["overlap"].append((item, a, b, clean(r[3]) if len(r) > 3 else ""))
            elif kind == "grades" and len(r) >= 3:
                g, rate, days = clean(r[0]), _num(r[1]), _num(r[2])
                if g and "blended" not in g.lower() and rate and days:
                    found["grades"].append((g, rate, days, clean(r[-1])))
            elif kind == "client" and len(r) >= 5:
                who, people, sess, hrs = clean(r[0]), _num(r[2]), _num(r[3]), _num(r[4])
                if who and not who.upper().startswith("TOTAL") and None not in (people, sess, hrs):
                    found["client"].append((who, clean(r[1]), people, sess, hrs,
                                            clean(r[6]) if len(r) > 6 else ""))
            elif kind == "scope" and len(r) >= 3:
                a, d = clean(r[0]), _num(r[2])
                if re.match(r"^A\d+$", a) and d:
                    found["scope"].append((a, clean(r[1]), d))
            elif kind == "ratecard" and len(r) >= 2:
                g, cost = clean(r[0]), _num(r[1])
                if g and cost is not None:
                    found["ratecard"].append((g, cost, _num(r[2]) if len(r) > 2 else None,
                                              clean(r[4]) if len(r) > 4 else ""))
            elif kind == "certain" and len(r) >= 2:
                n, v = clean(r[0]), _num(r[1])
                if n and not n.upper().startswith("TOTAL") and v:
                    found["certain"].append((n, v, clean(r[2]) if len(r) > 2 else ""))
    return found


# ── workbook construction ──────────────────────────────────────────────────────

def _style(ws, row, ncols, fill=None, bold=False, header=False):
    from openpyxl.styles import Font, PatternFill, Alignment
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        if header:
            cell.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
            cell.fill = PatternFill("solid", fgColor=HEAD_FILL)
            cell.alignment = Alignment(wrap_text=True, vertical="center")
        else:
            if bold:
                cell.font = Font(name=FONT, bold=True, size=10)
            if fill:
                cell.fill = PatternFill("solid", fgColor=fill)


def enforce_conventions(wb):
    """Apply the `xlsx` skill's model conventions across every sheet, in one pass.

    Threading font and colour through every write site is how one cell gets missed; doing it
    once at the end cannot miss any. Colour is derived from what the cell IS — a formula string
    means a formula, a cross-sheet reference means green — so it stays correct even when a cell
    changes kind later.
    """
    from openpyxl.styles import Font, PatternFill
    yellow = PatternFill("solid", fgColor=YELLOW)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                f = cell.font
                if f and f.color and f.color.rgb == "FFFFFFFF":
                    cell.font = Font(name=FONT, bold=True, color="FFFFFF", size=10)
                    continue                       # header band — leave it
                v = cell.value
                is_yellow = bool(cell.fill and cell.fill.fgColor
                                 and str(cell.fill.fgColor.rgb).endswith(YELLOW))
                if isinstance(v, str) and v.startswith("="):
                    colour = GREEN if "!" in v or any(
                        n in v for n in ("ratecard", "P50", "P80", "blended_rate", "rho",
                                         "nonlabour", "conf", "term_days", "low_", "max_marks",
                                         "sigma_cells", "pert_mean", "sum_", "costbase",
                                         "contingency_days", "scope_exposure", "rate_status")
                    ) else BLACK
                    cell.font = Font(name=FONT, size=10, bold=bool(f and f.bold), color=colour)
                elif is_yellow or (v is not None and not isinstance(v, str)):
                    # Yellow fill, or a typed literal, means an input — blue text either way.
                    cell.font = Font(name=FONT, size=10, bold=bool(f and f.bold), color=BLUE)
                    cell.fill = yellow
                else:
                    cell.font = Font(name=FONT, size=10, bold=bool(f and f.bold), color=BLACK)


def _widths(ws, widths):
    from openpyxl.utils import get_column_letter
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _named(wb, name, sheet, ref):
    from openpyxl.workbook.defined_name import DefinedName
    wb.defined_names.add(DefinedName(name, attr_text=f"'{sheet}'!{ref}"))


def build(data, rho, out_path, zero_rates=False):
    from openpyxl import Workbook

    wb = Workbook()
    eff = data["effort"] or [(f"S-{i:02d}", "<activity>", 0, 0, 0, "") for i in range(1, 4)]
    grades = data["grades"] or [("<grade>", 0, 0, "[⚠VERIFY]")]
    # A dedicated rate-card table wins; otherwise fall back to the rate column of the grades
    # table, so an estimate written before the rate card existed still produces a working model.
    ratecard = data.get("ratecard") or [(g, rate, None, src) for g, rate, _d, src in grades]
    client = data["client"] or [("<group>", "<activity>", 0, 0, 0, "")]
    scope = data["scope"] or [("A1", "<if wrong>", 0)]
    certain = data["certain"] or [("Financing", 0, ""), ("Travel", 0, ""), ("Production", 0, "")]

    # ── README ────────────────────────────────────────────────────────────────
    ws = wb.active
    ws.title = "README"
    _widths(ws, [110])
    for r, line in enumerate([
        "ESTIMATION MODEL — live formulas",
        "",
        "Yellow cells are INPUTS: change them. Blue cells are FORMULAS: everything recalculates.",
        "",
        "Sheet            What it does",
        "Inputs           Rates, non-labour, correlation assumption, competitor range. Start here.",
        "Effort           One row per scope item (S-ID) with three-point O/M/P. Expected + sigma are formulas.",
        "OverlapAudit     Record of days removed for double-counting. Cross-checks against Effort.",
        "Range            P50 / P80 from the three-point data. The CORRELATION cell drives the width — see Inputs.",
        "Grades           Grade x rate x days -> labour cost and the blended rate.",
        "ClientEffort     The client's hours. Required by some RFPs; scope protection either way.",
        "ScopeVariance    What each assumption costs if it is wrong. A DIFFERENT quantity from the P50/P80 band.",
        "Cost             Cost base at P50 and at P80. Stops before margin — pricing is a human decision.",
        "Decision         Candidate prices -> marks and margin. Deliberately recommends nothing.",
        "",
        "TWO UNCERTAINTIES, KEPT APART:",
        "  Range         = execution variance  (how long the work takes)   -> handled with contingency days",
        "  ScopeVariance = scope variance      (whether this IS the work)  -> handled with assumptions in the contract",
        "  Do not add them together. They are managed with different instruments.",
        "",
        "The correlation cell on Inputs matters more than it looks. Textbook PERT assumes line items",
        "are independent; on a decomposed consulting scope they share assumptions and a team, so when",
        "one is wrong several are wrong. If sigma looks implausibly tight, that cell is the reason.",
        "",
        "This workbook does not nominate a bid price. It supplies the tradeoff; the partner decides.",
    ], 1):
        ws.cell(row=r, column=1, value=line)
    ws.cell(row=1, column=1).font = __import__("openpyxl").styles.Font(bold=True, size=13)

    # ── Inputs ────────────────────────────────────────────────────────────────
    ws = wb.create_sheet("Inputs")
    _widths(ws, [42, 16, 62])
    ws.append(["Input", "Value", "Note"]); _style(ws, 1, 3, header=True)
    inputs = [
        ("Working days in term", 126, "After public holidays. Drives implied FTE.", "term_days"),
        ("Correlation assumption (rho)", rho,
         "0 = independent (textbook PERT, usually too tight) · 0.5 = partially correlated "
         "(professional-services default) · 1 = fully correlated", "rho"),
        ("Confidence level for the commitment number", 0.80,
         "0.80 = P80. Change to 0.70 or 0.90 to re-cut the range.", "conf"),
        ("Assumed lowest competitor bid — low", 225000, "An assumption. Say so in the narrative.", "low_a"),
        ("Assumed lowest competitor bid — mid", 240000, "", "low_b"),
        ("Assumed lowest competitor bid — high", 270000, "", "low_c"),
        ("Cost marks available", 300, "From the buyer's evaluation table.", "max_marks"),
    ]
    # Row numbers are tracked explicitly rather than inferred from len(). Mixing ws.append()
    # with ws.cell(row=N) moves openpyxl's internal cursor in a way that is easy to get wrong,
    # and the first version did: the `nonlabour` named range landed one row short of the SUM,
    # so the cost base silently omitted €11k. The workbook still opened and still looked right.
    row = 1
    for label, val, note, nm in inputs:
        row += 1
        ws.cell(row=row, column=1, value=label)
        ws.cell(row=row, column=2, value=val)
        ws.cell(row=row, column=3, value=note)
        _style(ws, row, 2, fill=INPUT_FILL)
        _named(wb, nm, "Inputs", f"$B${row}")
    row += 2
    ws.cell(row=row, column=1, value="Non-labour and certain costs").font = \
        __import__("openpyxl").styles.Font(bold=True)
    row += 1
    for c, h in enumerate(("Line", "€", "Basis"), 1):
        ws.cell(row=row, column=c, value=h)
    _style(ws, row, 3, header=True)
    cert_first = row + 1
    for name, val, basis in certain:
        row += 1
        ws.cell(row=row, column=1, value=name)
        ws.cell(row=row, column=2, value=val)
        ws.cell(row=row, column=3, value=basis)
        _style(ws, row, 2, fill=INPUT_FILL)
    cert_last = row
    row += 1
    ws.cell(row=row, column=1, value="Total non-labour + certain")
    ws.cell(row=row, column=2, value=f"=SUM(B{cert_first}:B{cert_last})")
    _style(ws, row, 2, fill=DERIVED_FILL, bold=True)
    ws.cell(row=row, column=2).number_format = EUR
    _named(wb, "nonlabour", "Inputs", f"$B${row}")

    # ── RateCard ──────────────────────────────────────────────────────────────
    # One table, one place. Rates typed inline against each grade row mean the day the real card
    # arrives you edit every row and hope you caught them all; here you paste one table and the
    # whole model recalculates. It doubles as the deliverable some tenders require in their own
    # right (an extension / call-off rate schedule), which is why sell rates sit alongside cost.
    ws = wb.create_sheet("RateCard")
    _widths(ws, [44, 18, 18, 16, 52])
    ws.cell(row=1, column=1, value="RATE CARD — the single source of every rate in this model")
    ws.cell(row=1, column=1).font = __import__("openpyxl").styles.Font(bold=True, size=12)
    ws.cell(row=2, column=1, value="Status")
    ws.cell(row=2, column=2, value="PLACEHOLDER")
    _style(ws, 2, 2, fill=INPUT_FILL, bold=True)
    ws.cell(row=2, column=3,
            value="Set to ACTUAL only when these are the firm's real published rates. "
                  "While it reads PLACEHOLDER, no price computed here may be committed.")
    _named(wb, "rate_status", "RateCard", "$B$2")
    for c, h in enumerate(("Grade", "Cost rate / day €", "Sell rate / day €",
                           "Effective date", "Source"), 1):
        ws.cell(row=4, column=c, value=h)
    _style(ws, 4, 5, header=True)
    rc_first = 5
    for i, (g, cost, sell, src) in enumerate(ratecard, rc_first):
        ws.cell(row=i, column=1, value=g)
        ws.cell(row=i, column=2, value=0 if zero_rates else cost)
        ws.cell(row=i, column=3, value=None if zero_rates else sell)
        ws.cell(row=i, column=4, value=None)
        ws.cell(row=i, column=5, value=src)
        _style(ws, i, 4, fill=INPUT_FILL)
        ws.cell(row=i, column=2).number_format = EUR
        ws.cell(row=i, column=3).number_format = EUR
    rc_last = rc_first + len(ratecard) - 1
    _named(wb, "ratecard", "RateCard", f"$A${rc_first}:$C${rc_last}")
    _named(wb, "ratecard_grades", "RateCard", f"$A${rc_first}:$A${rc_last}")
    for k, line in enumerate([
        "",
        "Grade names must match the Grades sheet exactly — that sheet looks rates up from here.",
        "A grade with no row here resolves to a rate of 0, and Grades flags it. Zero is a",
        "visible wrong answer; a lookup error spreading through the model is not.",
        "",
        "Sell rates are not used by the cost model (which runs on cost rates). They are here",
        "because a tender often has to submit a rate schedule for extension or call-off work,",
        "and that schedule should not be maintained in a second place.",
    ]):
        ws.cell(row=rc_last + 2 + k, column=1, value=line)

    # ── Effort ────────────────────────────────────────────────────────────────
    ws = wb.create_sheet("Effort")
    _widths(ws, [10, 46, 8, 8, 8, 12, 10, 24])
    ws.append(["S-ID", "Activity", "O", "M", "P", "Expected", "sigma", "Lead role"])
    _style(ws, 1, 8, header=True)
    for i, (sid, act, o, m, p, lead) in enumerate(eff, 2):
        ws.append([sid, act, o, m, p,
                   f"=(C{i}+4*D{i}+E{i})/6", f"=(E{i}-C{i})/6", lead])
        for col in ("C", "D", "E"):
            ws[f"{col}{i}"].fill = __import__("openpyxl").styles.PatternFill("solid", fgColor=INPUT_FILL)
        for col in ("F", "G"):
            ws[f"{col}{i}"].fill = __import__("openpyxl").styles.PatternFill("solid", fgColor=DERIVED_FILL)
            ws[f"{col}{i}"].number_format = "0.0"
    first, last = 2, len(eff) + 1
    tot = last + 1
    ws.append(["TOTAL", "", f"=SUM(C{first}:C{last})", f"=SUM(D{first}:D{last})",
               f"=SUM(E{first}:E{last})", f"=SUM(F{first}:F{last})",
               f"=SUM(G{first}:G{last})", ""])
    _style(ws, tot, 8, fill=DERIVED_FILL, bold=True)
    for nm, ref in (("sum_O", f"$C${tot}"), ("sum_M", f"$D${tot}"), ("sum_P", f"$E${tot}"),
                    ("pert_mean", f"$F${tot}")):
        _named(wb, nm, "Effort", ref)
    _named(wb, "sigma_cells", "Effort", f"$G${first}:$G${last}")
    ws.append([])
    ws.append(["Completeness sweep — booked somewhere above?", "", "", "", "", "", "", ""])
    _style(ws, tot + 2, 1, bold=True)
    for k, item in enumerate(["mobilisation", "governance / steering", "QA",
                              "document production", "client review cycles + rework"]):
        ws.append([""] + [item, "yes / no"])
        _style(ws, tot + 3 + k, 3, fill=INPUT_FILL)

    # ── OverlapAudit ──────────────────────────────────────────────────────────
    ws = wb.create_sheet("OverlapAudit")
    _widths(ws, [34, 12, 12, 12, 34, 56])
    ws.append(["Item", "Original", "Revised", "Deduction", "Pattern",
               "Why it re-uses another item's fieldwork"])
    _style(ws, 1, 6, header=True)
    ov = data["overlap"]
    for i, (item, a, b, why) in enumerate(ov or [("<item>", 0, 0, "")], 2):
        ws.append([item, a, b, f"=B{i}-C{i}", "", why])
        _style(ws, i, 3, fill=INPUT_FILL)
        ws[f"D{i}"].fill = __import__("openpyxl").styles.PatternFill("solid", fgColor=DERIVED_FILL)
    olast = max(2, len(ov) + 1)
    ws.append(["TOTAL DEDUCTION", f"=SUM(B2:B{olast})", f"=SUM(C2:C{olast})",
               f"=SUM(D2:D{olast})", "", ""])
    _style(ws, olast + 1, 6, fill=DERIVED_FILL, bold=True)
    ws.append([])
    ws.append(["Naive bottom-up (before audit)", f"=pert_mean+D{olast + 1}", "", "",
               "", "Cross-check: audited Effort total + deduction"])
    ws.append(["Audited (Effort!TOTAL Expected)", "=pert_mean", "", "", "", ""])
    for rr in (olast + 3, olast + 4):
        _style(ws, rr, 2, fill=DERIVED_FILL)
    ws.append([])
    ws.append(["Examined and KEPT (an audit that only ever cuts is a discount, not an audit)"])
    _style(ws, olast + 6, 1, bold=True)
    ws.append(["<item — genuinely separate fieldwork because …>"])

    # ── Range ─────────────────────────────────────────────────────────────────
    ws = wb.create_sheet("Range")
    _widths(ws, [46, 16, 76])
    ws.append(["Execution variance", "Days", "Note"]); _style(ws, 1, 3, header=True)
    rows = [
        ("sigma if INDEPENDENT (textbook PERT)", "=SQRT(SUMSQ(sigma_cells))",
         "Assumes line items are unrelated. On a decomposed consulting scope they are not."),
        ("sigma if FULLY CORRELATED", "=SUM(sigma_cells)",
         "Every item hangs on the same handful of assumptions."),
        ("sigma USED (rho from Inputs)", "=IFERROR(SQRT(B2^2+rho*(B3^2-B2^2)),0)",
         "Change rho on Inputs. If sigma looks implausibly tight, rho is the reason."),
        ("z for the confidence level", "=NORMSINV(conf)",
         "0.8416 at P80. Replace with a constant if your spreadsheet lacks NORMSINV."),
        ("Sum O (everything goes right)", "=sum_O", ""),
        ("Sum M (most likely)", "=sum_M", ""),
        ("Sum P (everything goes wrong)", "=sum_P", ""),
        ("P50 — the planning number", "=pert_mean", "PERT mean."),
        ("P80 — the commitment number", "=B9+B5*B4", "P50 + z * sigma."),
        ("Contingency (P80 - P50)", "=B10-B9", "This IS the contingency. Do not also hand-pick risk lines."),
        ("Implied FTE at P50", "=IFERROR(B9/term_days,0)", "Compare against the team actually being named."),
    ]
    for i, (label, f, note) in enumerate(rows, 2):
        ws.append([label, f, note])
        _style(ws, i, 2, fill=DERIVED_FILL)
        ws.cell(row=i, column=2).number_format = "0.0"
    for nm, ref in (("P50", "$B$9"), ("P80", "$B$10"), ("contingency_days", "$B$11")):
        _named(wb, nm, "Range", ref)
    _style(ws, 9, 3, bold=True); _style(ws, 10, 3, bold=True)

    # ── Grades ────────────────────────────────────────────────────────────────
    ws = wb.create_sheet("Grades")
    _widths(ws, [44, 18, 10, 16, 30])
    for c, h in enumerate(("Grade", "Cost rate / day (from RateCard)", "Days", "Cost", "Check"), 1):
        ws.cell(row=1, column=c, value=h)
    _style(ws, 1, 5, header=True)
    for i, (g, _rate, days, _src) in enumerate(grades, 2):
        ws.cell(row=i, column=1, value=g)
        ws.cell(row=i, column=2, value=f"=IFERROR(VLOOKUP(A{i},ratecard,2,FALSE),0)")
        ws.cell(row=i, column=3, value=days)
        ws.cell(row=i, column=4, value=f"=B{i}*C{i}")
        ws.cell(row=i, column=5,
                value=f'=IF(COUNTIF(ratecard_grades,A{i})=0,"NOT IN RATE CARD","")')
        _style(ws, i, 1, fill=INPUT_FILL)          # grade name is an input …
        _style(ws, i, 3, fill=INPUT_FILL)          # … so are days
        ws[f"C{i}"].fill = __import__("openpyxl").styles.PatternFill("solid", fgColor=INPUT_FILL)
        for c in ("B", "D", "E"):
            ws[f"{c}{i}"].fill = __import__("openpyxl").styles.PatternFill("solid", fgColor=DERIVED_FILL)
        ws[f"B{i}"].number_format = '#,##0'
        ws[f"D{i}"].number_format = EUR
    glast = len(grades) + 1
    tot = glast + 1
    ws.cell(row=tot, column=1, value="BLENDED / TOTAL")
    # IFERROR, not a bare division: with a zeroed rate card or an empty grade list this must
    # return 0, not spray #DIV/0! through every sheet that depends on the blended rate.
    ws.cell(row=tot, column=2, value=f"=IFERROR(D{tot}/C{tot},0)")
    ws.cell(row=tot, column=3, value=f"=SUM(C2:C{glast})")
    ws.cell(row=tot, column=4, value=f"=SUM(D2:D{glast})")
    _style(ws, tot, 5, fill=DERIVED_FILL, bold=True)
    ws[f"B{tot}"].number_format = EUR
    ws[f"D{tot}"].number_format = EUR
    _named(wb, "blended_rate", "Grades", f"$B${tot}")
    _named(wb, "grade_days", "Grades", f"$C${tot}")
    ws.cell(row=tot + 2, column=1, value="Allocated days must equal P50")
    ws.cell(row=tot + 2, column=2, value=f'=IF(ABS(C{tot}-P50)<0.5,"OK","MISMATCH")')
    ws.cell(row=tot + 2, column=5, value="Re-allocate the grade mix when P50 moves.")
    _style(ws, tot + 2, 2, fill=DERIVED_FILL, bold=True)
    ws.cell(row=tot + 3, column=1, value="Rate card status")
    ws.cell(row=tot + 3, column=2, value="=rate_status")
    ws.cell(row=tot + 3, column=5, value="ACTUAL required before any price is committed.")
    _style(ws, tot + 3, 2, fill=DERIVED_FILL, bold=True)

    # ── ClientEffort ──────────────────────────────────────────────────────────
    ws = wb.create_sheet("ClientEffort")
    _widths(ws, [40, 42, 10, 11, 13, 13, 16])
    ws.append(["Their role / group", "Activity", "People", "Sessions", "Hours each",
               "Total hours", "When"])
    _style(ws, 1, 7, header=True)
    for i, (who, act, people, sess, hrs, when) in enumerate(client, 2):
        ws.append([who, act, people, sess, hrs, f"=C{i}*D{i}*E{i}", when])
        _style(ws, i, 5, fill=INPUT_FILL)
        ws[f"F{i}"].fill = __import__("openpyxl").styles.PatternFill("solid", fgColor=DERIVED_FILL)
    clast = len(client) + 1
    ws.append(["TOTAL", "", "", "", "", f"=SUM(F2:F{clast})", ""])
    _style(ws, clast + 1, 7, fill=DERIVED_FILL, bold=True)
    ws.append(["Client days (hrs / 7.5)", "", "", "", "", f"=F{clast + 1}/7.5", ""])
    ws.append(["Client-to-consultant ratio", "", "", "", "", f"=IFERROR(F{clast + 2}/P50,0)",
               "10–15% is normal for a workshop-led assessment"])
    ws[f"F{clast + 3}"].number_format = "0.0%"
    for rr in (clast + 2, clast + 3):
        _style(ws, rr, 6, fill=DERIVED_FILL)

    # ── ScopeVariance ─────────────────────────────────────────────────────────
    ws = wb.create_sheet("ScopeVariance")
    _widths(ws, [12, 62, 12, 16, 40])
    ws.append(["Assumption", "If wrong", "Days", "€", "Disposition"])
    _style(ws, 1, 5, header=True)
    for i, (a, why, d) in enumerate(scope, 2):
        ws.append([a, why, d, f"=C{i}*blended_rate", "excluded by assumption / accepted"])
        _style(ws, i, 3, fill=INPUT_FILL)
        ws[f"D{i}"].fill = __import__("openpyxl").styles.PatternFill("solid", fgColor=DERIVED_FILL)
        ws[f"D{i}"].number_format = EUR
    slast = len(scope) + 1
    ws.append(["TOTAL", "Upside exposure — carried by ASSUMPTIONS, not by days",
               f"=SUM(C2:C{slast})", f"=SUM(D2:D{slast})", ""])
    _style(ws, slast + 1, 5, fill=DERIVED_FILL, bold=True)
    _named(wb, "scope_exposure_eur", "ScopeVariance", f"$D${slast + 1}")
    ws.append([])
    ws.append(["Scope band ÷ execution band", f"=IFERROR(C{slast + 1}/contingency_days,0)", "",
               "", "If this is >1, scope definition is the dominant risk — not execution."])
    _style(ws, slast + 3, 2, fill=DERIVED_FILL, bold=True)
    ws.cell(row=slast + 3, column=2).number_format = MULT

    # ── Cost ──────────────────────────────────────────────────────────────────
    ws = wb.create_sheet("Cost")
    _widths(ws, [42, 18, 18, 56])
    ws.append(["Line", "at P50 €", "at P80 €", "Note"]); _style(ws, 1, 4, header=True)
    ws.append(["Labour", "=P50*blended_rate", "=P80*blended_rate", "Days x blended cost rate"])
    ws.append(["Non-labour + certain costs", "=nonlabour", "=nonlabour", "From Inputs"])
    ws.append(["COST BASE", "=B2+B3", "=C2+C3", "Margin is NOT set here — pricing is a human decision"])
    ws.append(["Rate card status", "=rate_status", "",
               '=IF(rate_status<>"ACTUAL","⚠ PLACEHOLDER RATES — this cost base is not committable","")'])
    for rr in (2, 3, 4):
        _style(ws, rr, 3, fill=DERIVED_FILL)
        for c in ("B", "C"):
            ws[f"{c}{rr}"].number_format = EUR
    _style(ws, 4, 4, bold=True)
    _named(wb, "costbase_P50", "Cost", "$B$4")
    _named(wb, "costbase_P80", "Cost", "$C$4")

    # ── Decision ──────────────────────────────────────────────────────────────
    ws = wb.create_sheet("Decision")
    _widths(ws, [18, 18, 18, 18, 14, 18, 30])
    ws.append(["Candidate price", "Marks if lowest = low", "if mid", "if high",
               "Margin vs P50", "Margin €", "Flag"])
    _style(ws, 1, 7, header=True)
    for i in range(2, 8):
        # IFERROR as well as the blank guard: the blank test stops an empty row, but a reviewer
        # typing 0 into a candidate-price cell would still divide by zero and spray #DIV/0!
        # across the row they are in the middle of filling in.
        ws.append([
            None,
            f"=IFERROR(IF(A{i}=\"\",\"\",MIN(low_a/A{i},1)*max_marks),\"\")",
            f"=IFERROR(IF(A{i}=\"\",\"\",MIN(low_b/A{i},1)*max_marks),\"\")",
            f"=IFERROR(IF(A{i}=\"\",\"\",MIN(low_c/A{i},1)*max_marks),\"\")",
            f"=IFERROR(IF(A{i}=\"\",\"\",(A{i}-costbase_P50)/A{i}),\"\")",
            f"=IF(A{i}=\"\",\"\",A{i}-costbase_P50)",
            f'=IF(A{i}="","",IF(A{i}<costbase_P50,"UNDER COST BASE",'
            f'IF(A{i}<costbase_P80,"contingency not covered",'
            f'IF(A{i}-costbase_P50<scope_exposure_eur,"margin < excluded scope exposure","")))) ',
        ])
        _style(ws, i, 1, fill=INPUT_FILL)
        for c in ("B", "C", "D", "E", "F", "G"):
            ws[f"{c}{i}"].fill = __import__("openpyxl").styles.PatternFill("solid", fgColor=DERIVED_FILL)
        for c in ("B", "C", "D"):
            ws[f"{c}{i}"].number_format = "0.0"
        ws[f"E{i}"].number_format = PCT
        ws[f"F{i}"].number_format = EUR
    ws.append([])
    for k, line in enumerate([
        "Type candidate prices into column A. Everything else is a formula.",
        "Marks formula caps the ratio at 1: below the lowest bid you score full marks, not more.",
        "",
        "THIS SHEET DELIBERATELY RECOMMENDS NOTHING. Pricing weighs client appetite, competitive",
        "position and risk tolerance that this model does not contain. Record the decision, once",
        "taken, in _pm/raid_and_decisions.md.",
    ]):
        ws.cell(row=9 + k, column=1, value=line)
    ws.cell(row=12, column=1).font = __import__("openpyxl").styles.Font(bold=True)

    enforce_conventions(wb)
    wb.save(out_path)
    return {k: len(v) for k, v in data.items()}


# ── arithmetic audit of the markdown itself ────────────────────────────────────

def check(data, rho):
    """Recompute in Python and report where the markdown disagrees with its own inputs."""
    eff = data["effort"]
    missing = [k for k in TABLE_KINDS if not data[k]]
    if missing:
        print(f"  ⚠ no rows found for: {', '.join(missing)} "
              f"— is the <!--table:KIND--> marker present above each table?")
    if not eff:
        print("  no effort table — nothing to check")
        return 1
    sO, sM, sP = (sum(r[i] for r in eff) for i in (2, 3, 4))
    mean = sum((o + 4 * m + p) / 6 for _, _, o, m, p, _ in eff)
    si = math.sqrt(sum(((p - o) / 6) ** 2 for _, _, o, m, p, _ in eff))
    sc = sum((p - o) / 6 for _, _, o, m, p, _ in eff)
    sd = math.sqrt(si ** 2 + rho * (sc ** 2 - si ** 2))
    exec_band = 0.8416 * sd
    print(f"  effort rows       {len(eff)}")
    print(f"  Sum O / M / P     {sO:.0f} / {sM:.0f} / {sP:.0f}")
    print(f"  PERT mean (P50)   {mean:.1f}")
    print(f"  sigma             indep {si:.1f} · rho={rho} {sd:.1f} · full {sc:.1f}")
    print(f"  P80               {mean + exec_band:.1f}   contingency {exec_band:.1f} d")
    if data["overlap"]:
        # The audit operates on the most-likely column, so the naive baseline is Sum M + the
        # deduction — not the PERT mean, which is a different statistic.
        ded = sum(a - b for _, a, b, _ in data["overlap"])
        print(f"  overlap deduction {ded:.0f} d  (naive Sum M {sM + ded:.0f} → audited {sM:.0f})")
    if data["grades"]:
        gd = sum(g[2] for g in data["grades"])
        lab = sum(g[1] * g[2] for g in data["grades"])
        print(f"  grade days        {gd:.0f}   labour {lab:,.0f}   blended {lab / gd:,.0f}")
        if abs(gd - mean) > 0.5:
            print(f"  ⚠ grade days {gd:.0f} != P50 {mean:.1f} — re-allocate the grade mix")
    if data["scope"]:
        sv = sum(s[2] for s in data["scope"])
        print(f"  scope band        {sv:.0f} d vs execution band {exec_band:.1f} d "
              f"→ {sv / exec_band:.1f}x")
    if data["client"]:
        hrs = sum(c[2] * c[3] * c[4] for c in data["client"])
        print(f"  client hours      {hrs:.0f}  ({hrs / 7.5:.1f} client-days, "
              f"{hrs / 7.5 / mean * 100:.1f}% of our effort)")
    return 0


def find_recalc():
    """Locate the `xlsx` skill's recalc.py. We do NOT reimplement recalculation.

    openpyxl writes formulas with no cached values, so a workbook straight out of this script
    reads back as `None` to anything looking at values — and, worse, a formula that LibreOffice
    cannot evaluate bakes a literal `#NAME?` into the file we hand over. The `xlsx` skill already
    owns that problem properly: a LibreOffice macro pass that rewrites the file in place and
    returns a JSON verdict with the failing cells named. A `soffice --convert-to` call (the
    obvious hand-rolled substitute, and the one this script shipped with first) converts the file
    but reports no formula errors at all — it looks like verification and is not.
    """
    env = os.environ.get("XLSX_SKILL_DIR")
    roots = [pathlib.Path(env)] if env else []
    roots += list(pathlib.Path.home().glob(
        ".claude/plugins/marketplaces/*/skills/xlsx"))
    roots += list(pathlib.Path.home().glob(".claude/skills/xlsx"))
    for r in roots:
        c = r / "scripts" / "recalc.py"
        if c.exists():
            return c
    return None


def recalculate(path):
    """Run the xlsx skill's recalc and surface its verdict. Returns True when the file is clean."""
    script = find_recalc()
    if not script:
        print("\n  ⚠ Could not find the `xlsx` skill's scripts/recalc.py.")
        print("    Formulas are written but NOT yet evaluated, and an unevaluated workbook can")
        print("    hide a #NAME?/#REF! until the client opens it.")
        print("    → Invoke the `xlsx` skill to recalculate, or set XLSX_SKILL_DIR.")
        print("    Do NOT substitute `soffice --convert-to`: it reports no formula errors.")
        return False
    import json
    import subprocess
    r = subprocess.run([sys.executable, str(script), os.path.abspath(path)],
                       capture_output=True, text=True, cwd=str(script.parent))
    try:
        v = json.loads(r.stdout[r.stdout.index("{"):r.stdout.rindex("}") + 1])
    except Exception:
        print(f"\n  ⚠ recalc.py produced no JSON verdict:\n{r.stdout[-500:]}{r.stderr[-500:]}")
        return False
    if v.get("status") == "success":
        print(f"\n  ✓ recalculated via the xlsx skill — {v.get('total_formulas', '?')} formulas, "
              f"0 errors")
        return True
    print(f"\n  ✗ recalc reports {v.get('total_errors', '?')} formula error(s): "
          f"{v.get('error_summary')}")
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("markdown", nargs="?", help="estimation.md to seed the workbook from")
    ap.add_argument("--out", help="output .xlsx (default: alongside the markdown)")
    ap.add_argument("--blank", action="store_true", help="starter workbook, no markdown needed")
    ap.add_argument("--rho", type=float, default=0.5,
                    help="correlation assumption, 0–1 (default 0.5, the professional-services default)")
    ap.add_argument("--zero-rates", action="store_true",
                    help="emit the rate card with every rate at 0 — use when no rate card exists "
                         "and a fabricated placeholder would be worse than a visible zero")
    ap.add_argument("--no-recalc", action="store_true",
                    help="skip the xlsx-skill recalculation pass (leaves formulas unevaluated)")
    ap.add_argument("--check", action="store_true",
                    help="recompute the markdown's arithmetic and report; write nothing")
    args = ap.parse_args()

    if not args.blank and not args.markdown:
        ap.error("give an estimation.md, or --blank for a starter workbook")

    data = {"effort": [], "overlap": [], "grades": [], "client": [], "scope": [], "certain": []}
    if args.markdown:
        if not os.path.exists(args.markdown):
            print(f"ERROR: not found: {args.markdown}", file=sys.stderr)
            return 2
        with open(args.markdown, encoding="utf-8", errors="replace") as f:
            data = parse_tables(f.read())

    if args.check:
        return check(data, args.rho)

    out = args.out or (os.path.splitext(args.markdown)[0] + ".xlsx" if args.markdown
                       else "estimation.xlsx")
    try:
        counts = build(data, args.rho, out, args.zero_rates)
    except ImportError:
        print("ERROR: openpyxl not installed — run: pip install openpyxl "
              "(PEP-668: add --user --break-system-packages)", file=sys.stderr)
        return 3
    print(f"Wrote {out}")
    for k, n in counts.items():
        print(f"  {k:9s} {n} row(s)" + ("   ← empty, using placeholders" if not n else ""))
    clean = True if args.no_recalc else recalculate(out)
    print("\nBlue text on yellow = input · black = formula · green = cross-sheet "
          "(the `xlsx` skill's model conventions).")
    print("The workbook is now the model — edit there, and keep the markdown in step with it.")
    return 0 if clean else 4


if __name__ == "__main__":
    sys.exit(main())
