"""The model drawn as a sheet: the recursion as nested frames, each level's
five functions, the requisite-variety test per plant, and the algedonic
channel as the route each alarm took to the top.

Deterministic SVG, drawn from the model objects and nothing else, with a
title block in the scenario format (programme, area, procedure, record).
A drawing shows the model's own structure; it proves nothing about a real
organisation.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .algedonic import AlgedonicEvent
from .system import System1, ViableSystem
from .variety import RequisiteResult

INK = "#111111"
INK2 = "#6b6b6b"
RULE = "#d4d4d4"
PAPER = "#ffffff"
PAPER2 = "#f4f4f4"
ACCENT = "#0000ee"
FONT = "IBM Plex Mono, ui-monospace, Menlo, monospace"

BAND = 22  # the strip that carries S5 S4 S3 3* S2
PAD = 10
LEAF_H = 44
GAP = 8


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;")


def _text(x: float, y: float, s: str, size: float = 10, fill: str = INK, anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
        f'fill="{fill}" text-anchor="{anchor}">{_esc(s)}</text>'
    )


@dataclass
class _Box:
    x: float
    y: float
    w: float
    h: float


class _Layout:
    """Where everything landed, so the algedonic routes can be drawn after."""

    def __init__(self) -> None:
        self.units: dict[str, _Box] = {}
        self.systems: dict[str, _Box] = {}
        self.s5: dict[str, _Box] = {}


def _height(s: ViableSystem) -> float:
    inner = max((_unit_height(u) for u in s.operations), default=LEAF_H)
    return BAND + PAD + inner + PAD


def _unit_height(u: System1) -> float:
    if u.subsystem is None:
        return LEAF_H
    return 18 + _height(u.subsystem) + 6


def _draw_system(s: ViableSystem, x: float, y: float, w: float, lay: _Layout) -> str:
    h = _height(s)
    lay.systems[s.name] = _Box(x, y, w, h)
    out = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{INK}" stroke-width="1"/>'
    # the meta-functions, right to left so S5 sits at the right edge
    out += _text(x + 6, y + 14, s.name, 9, INK)
    cells = [("S5", s.s5), ("S4", s.s4), ("S3", s.s3), ("3*", s.s3_star), ("S2", s.s2)]
    cw = 24.0
    for i, (label, present) in enumerate(cells):
        cx = x + w - 6 - (i + 1) * (cw + 3)
        fill = PAPER if present else ACCENT
        out += f'<rect x="{cx:.1f}" y="{y + 4:.1f}" width="{cw}" height="{BAND - 8}" fill="{fill}" stroke="{INK if present else ACCENT}" stroke-width="0.8"/>'
        out += _text(cx + cw / 2, y + 14, label if present else "!" + label, 7.5, INK if present else PAPER, "middle")
        if label == "S5":
            lay.s5[s.name] = _Box(cx, y + 4, cw, BAND - 8)
    out += f'<line x1="{x:.1f}" y1="{y + BAND:.1f}" x2="{x + w:.1f}" y2="{y + BAND:.1f}" stroke="{RULE}"/>'
    # the operations, side by side
    n = max(1, len(s.operations))
    uw = (w - 2 * PAD - (n - 1) * GAP) / n
    ux, uy = x + PAD, y + BAND + PAD
    for u in s.operations:
        out += _draw_unit(u, ux, uy, uw, lay)
        ux += uw + GAP
    return out


def _draw_unit(u: System1, x: float, y: float, w: float, lay: _Layout) -> str:
    h = _unit_height(u)
    lay.units[u.id] = _Box(x, y, w, h)
    out = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPER2}" stroke="{RULE}"/>'
    out += _text(x + 6, y + 13, f"{u.id}  productivity {u.metrics.productivity:.2f}", 8, INK)
    if u.subsystem is None:
        # the triple vector as three ticks on one bar: actuality, capability, potentiality
        bx, by, bw = x + 6, y + 26, w - 12
        out += f'<line x1="{bx:.1f}" y1="{by}" x2="{bx + bw:.1f}" y2="{by}" stroke="{RULE}" stroke-width="4"/>'
        out += f'<line x1="{bx:.1f}" y1="{by}" x2="{bx + bw * u.metrics.performance:.1f}" y2="{by}" stroke="{INK}" stroke-width="4"/>'
        for frac, label in ((u.metrics.performance, "a"), (u.metrics.latency, "c"), (1.0, "p")):
            tx = bx + bw * frac
            out += f'<line x1="{tx:.1f}" y1="{by - 5}" x2="{tx:.1f}" y2="{by + 5}" stroke="{INK}" stroke-width="0.8"/>'
            out += _text(tx, by + 14, label, 7, INK2, "middle")
        return out
    out += _draw_system(u.subsystem, x + 6, y + 18, w - 12, lay)
    return out


def sheet(
    root: ViableSystem,
    requisite_rows: Sequence[tuple[str, RequisiteResult]] = (),
    events: Sequence[AlgedonicEvent] = (),
    *,
    threshold: float | None = None,
    timeout: int | None = None,
    width: float = 760,
) -> str:
    """Draw ``root`` with its requisite tests and alarms as one SVG sheet."""
    pad = 48
    lay = _Layout()
    gh = _height(root)
    meter_h = 26 * len(requisite_rows) + (16 if requisite_rows else 0)
    block = 150
    w_total = width + pad * 2
    h_total = pad + gh + 30 + meter_h + 30 + block + pad
    body = _text(pad, pad - 14, f"viable system / {root.name} / depth {root.depth()}", 10, INK2)
    body += _text(pad + width, pad - 14, "benmicallef / viable-system-model / drawn by the library", 10, INK2, "end")
    body += _draw_system(root, pad, pad, width, lay)
    # the algedonic channel: each alarm as a route from its unit to the root's System 5
    top = lay.s5[root.name]
    drawn: set[str] = set()
    for e in events:
        box = lay.units.get(e.unit_id)
        if box is None or e.unit_id in drawn:
            continue
        drawn.add(e.unit_id)
        x0, y0 = box.x + box.w / 2, box.y + box.h
        x1, y1 = top.x + top.w / 2, top.y + top.h
        ticks = sorted({ev.tick for ev in events if ev.unit_id == e.unit_id})
        body += (
            f'<path d="M{x0:.1f} {y0:.1f}v8H{x1 + 300:.1f}V{y1 - 2:.1f}H{x1:.1f}V{y1:.1f}" '
            f'fill="none" stroke="{ACCENT}" stroke-width="1.2" stroke-dasharray="4 3"/>'
        )
        body += f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="3" fill="{ACCENT}"/>'
        body += _text(x0 + 6, y0 + 18, f"alarm, tick {', '.join(str(t) for t in ticks)} — to System 5", 8, ACCENT)
    # requisite variety per named system: disturbance against regulator, in bits
    my = pad + gh + 30
    if requisite_rows:
        body += _text(pad, my, "requisite variety, in bits (disturbance above, regulator below; the shortfall in blue)", 9, INK2)
        scale = width * 0.5 / max(max(r.disturbance_bits, r.regulator_bits) for _, r in requisite_rows)
        for i, (label, r) in enumerate(requisite_rows):
            y = my + 16 + i * 26
            body += _text(pad, y + 9, label, 9, INK)
            bx = pad + 160
            body += f'<rect x="{bx}" y="{y}" width="{r.disturbance_bits * scale:.1f}" height="5" fill="{INK2}"/>'
            body += f'<rect x="{bx}" y="{y + 7}" width="{r.regulator_bits * scale:.1f}" height="5" fill="{INK}"/>'
            if not r.is_requisite:
                body += (
                    f'<rect x="{bx + r.regulator_bits * scale:.1f}" y="{y + 7}" '
                    f'width="{(r.disturbance_bits - r.regulator_bits) * scale:.1f}" height="5" fill="{ACCENT}"/>'
                )
            verdict = "requisite" if r.is_requisite else f"short by {r.deficit_bits:.0f} bits"
            body += _text(bx + max(r.disturbance_bits, r.regulator_bits) * scale + 8, y + 10, f"{r.disturbance_bits:.0f} / {r.regulator_bits:.0f} — {verdict}", 8, INK2)
    # title block, scenario format
    leaves = [u for _, u in root.walk() if u.subsystem is None]
    alarmed = sorted({e.unit_id for e in events})
    short = [label for label, r in requisite_rows if not r.is_requisite]
    rows = [
        ("project", f"viable-system-model — {root.name}, drawn by the library"),
        ("programme", f"a recursion of depth {root.depth()}: {len(root.operations)} units at the top, {len(leaves)} at the leaves; "
                      f"functions 2, 3, 3*, 4 and 5 {'present at every level' if root.is_structurally_viable() else 'MISSING somewhere: ' + ', '.join(root.missing_functions())}"),
        ("area", f"{len(list(root.walk()))} operational units in all; each leaf shows actuality (a), capability (c), potentiality (p) on one bar"),
        ("procedure", "variety is log2 of the states a thing can take; a regulator is requisite when it has at least the disturbance's variety (Ashby); "
                      + (f"an alarm escalates straight to System 5 when productivity stays below {threshold} for {timeout} readings (Beer's algedonic channel)" if threshold is not None else "alarms escalate straight to System 5 (Beer's algedonic channel)")),
        ("record", f"structurally viable: {'yes' if root.is_structurally_viable() else 'no'} / "
                   f"{'short of variety: ' + ', '.join(short) if short else 'every regulator requisite'} / "
                   f"{len(events)} alarms{' from ' + ', '.join(alarmed) if alarmed else ''}"),
    ]
    ty = my + meter_h + 30
    body += f'<line x1="{pad}" y1="{ty - 14}" x2="{pad + width}" y2="{ty - 14}" stroke="{RULE}"/>'
    max_chars = int((width - 90) / 6)
    y = ty
    for key, value in rows:
        lines: list[str] = []
        cur = ""
        for word in value.split(" "):
            if cur and len(cur) + 1 + len(word) > max_chars:
                lines.append(cur)
                cur = word
            else:
                cur = f"{cur} {word}" if cur else word
        if cur:
            lines.append(cur)
        body += _text(pad, y, key, 10, INK2)
        for i, line in enumerate(lines):
            body += _text(pad + 90, y + i * 13, line, 10, INK)
        y += len(lines) * 13 + 5
    h_total = max(h_total, y + pad)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w_total:.0f} {h_total:.0f}" width="{w_total:.0f}" height="{h_total:.0f}" '
        f'role="img" aria-label="viable system sheet, {_esc(root.name)}">\n'
        f'<rect width="{w_total:.0f}" height="{h_total:.0f}" fill="{PAPER}"/>\n'
        f'<rect x="0.5" y="0.5" width="{w_total - 1:.0f}" height="{h_total - 1:.0f}" fill="none" stroke="{RULE}"/>\n'
        f"{body}\n</svg>\n"
    )
