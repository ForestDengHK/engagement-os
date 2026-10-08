#!/usr/bin/env python3
"""Read commitments-register values from a build script, so no commitment is ever a literal.

A deck build that types "24 months" on a slide keeps saying it after the register moves to
12 months. A build that asks the register cannot:

    import sys; sys.path.insert(0, "<plugin>/skills/eng-os/scripts")
    import commitments
    commitments.load(repo_root)                       # or the path of commitments.md
    hold = commitments.value("C-07")                  # "fixed until 31 December 2027"
    until = commitments.date_of("C-07")               # datetime.date(2027, 12, 31)

`/eng-sync`'s deck-drift check proves every value on a slide equals the register.
"""
import datetime as dt
import os
import pathlib
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sync_commitments as scm

MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]
DMY_RE = re.compile(r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{4})\b", re.I)
ISO_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")

_rows = None


def _register_path(where):
    p = pathlib.Path(where).resolve()
    if p.is_file():
        return p
    found = scm.register_paths(p)
    if len(found) != 1:
        raise FileNotFoundError(
            f"{p}: expected one 01_pursuit/*/{scm.REGISTER_REL}, found {len(found)} — "
            "pass the register path itself")
    return found[0]


def load(where):
    """Load the register (a repo root, or the commitments.md path). Returns {ID: row}, each row
    keyed id · topic · class · value · applied · basis · approver · status · sections · slides."""
    global _rows
    reg = scm.Register(_register_path(where))
    _rows = {r["id"]: {k: v for k, v in r.items() if not k.startswith("_")} for r in reg.rows}
    return _rows


def _row(cid):
    if _rows is None:
        raise RuntimeError("commitments.load(<repo root>) first")
    if cid not in _rows:
        raise KeyError(f"{cid} is not in the commitments register")
    return _rows[cid]


def value(cid, default=None):
    """The exact string the response states for `cid`. An unknown id is always a KeyError (a
    typo must not ship); an empty Value is a ValueError unless a `default` is given."""
    v = _row(cid)["value"]
    if not v:
        if default is not None:
            return default
        raise ValueError(f"{cid} has an empty Value in the commitments register")
    return v


def date_of(cid):
    """The date inside `cid`'s Value — `31 December 2027` or `2027-12-31` — as a datetime.date."""
    v = value(cid)
    m = DMY_RE.search(v)
    if m:
        return dt.date(int(m.group(3)), MONTHS.index(m.group(2).lower()) + 1, int(m.group(1)))
    m = ISO_RE.search(v)
    if m:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    raise ValueError(f"{cid}: no 'D Month YYYY' or ISO date in its Value \"{v}\"")
