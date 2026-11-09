"""Deterministic text rendering of a viable system and its algedonic trace.

Plain ASCII, stable ordering, no colour — so the output can be snapshot-tested
and diffed. A rendering shows the model's own output and nothing more; an
org chart proves nothing about real viability.
"""

from __future__ import annotations

from collections.abc import Sequence

from .algedonic import AlgedonicEvent
from .system import System1, ViableSystem
from .variety import RequisiteResult


def _flags(s: ViableSystem) -> str:
    parts = [
        ("S2", s.s2),
        ("S3", s.s3),
        ("S3*", s.s3_star),
        ("S4", s.s4),
        ("S5", s.s5),
    ]
    return "[" + " ".join(name if present else "!" + name for name, present in parts) + "]"


def _render_unit(u: System1, prefix: str, last: bool, out: list[str]) -> None:
    branch = "`- " if last else "|- "
    line = f"{prefix}{branch}{u.id}  productivity {u.metrics.productivity:.2f}"
    if u.subsystem is not None:
        line += f"  {_flags(u.subsystem)}"
    out.append(line)
    if u.subsystem is not None:
        child_prefix = prefix + ("   " if last else "|  ")
        ops = u.subsystem.operations
        for i, child in enumerate(ops):
            _render_unit(child, child_prefix, i == len(ops) - 1, out)


def render_tree(root: ViableSystem) -> str:
    """The recursion as an indented tree, with each level's functions."""
    out: list[str] = [f"{root.name}  {_flags(root)}"]
    for i, u in enumerate(root.operations):
        _render_unit(u, "", i == len(root.operations) - 1, out)
    return "\n".join(out)


def render_requisite(rows: Sequence[tuple[str, RequisiteResult]]) -> str:
    """A table of requisite-variety tests, one row per (label, result)."""
    width = max((len(label) for label, _ in rows), default=4)
    out = [f"{'unit'.ljust(width)}  disturbance  regulator  requisite  deficit"]
    for label, r in rows:
        out.append(
            f"{label.ljust(width)}  {r.disturbance_bits:>11.2f}  {r.regulator_bits:>9.2f}  "
            f"{'yes' if r.is_requisite else 'NO ':>9}  {r.deficit_bits:>7.2f}"
        )
    return "\n".join(out)


def render_events(events: Sequence[AlgedonicEvent]) -> str:
    """One line per algedonic alarm, in deterministic order."""
    if not events:
        return "(no algedonic events)"
    out: list[str] = []
    for e in events:
        route = " -> ".join(e.path)
        out.append(f"ALGEDONIC  t={e.tick}  {e.unit_id}  productivity {e.productivity:.2f}  via {route}")
    return "\n".join(out)
