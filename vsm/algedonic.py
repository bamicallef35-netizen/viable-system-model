"""The algedonic channel: pain and pleasure signals that bypass the hierarchy.

Beer named the channel from the Greek *algos* (pain) and *hedone* (pleasure).
When an operational unit's performance departs from what it is capable of
and stays there, an alarm escalates straight up the recursion to System 5,
without waiting for the normal 1 → 2 → 3 routing.

Beer described the channel informally; he gave no algorithm. The rule here
— a *threshold* on productivity held for a *timeout* of consecutive readings
— is my operationalization, labelled as such. It is deterministic: the
events are a pure function of the readings, and are ordered by
(tick, depth, unit id) so two runs can be compared exactly.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .system import ViableSystem


@dataclass(frozen=True)
class AlgedonicEvent:
    """One alarm: which unit, when, how bad, and the route it escalates along."""

    tick: int
    unit_id: str
    productivity: float
    path: tuple[str, ...]  # from the unit's own system up to the root (System 5)

    @property
    def depth(self) -> int:
        return len(self.path)


def propagate(
    root: ViableSystem,
    readings: Mapping[str, Sequence[float]],
    *,
    threshold: float,
    timeout: int,
) -> list[AlgedonicEvent]:
    """Scan per-unit productivity readings and emit algedonic events.

    For each unit, an event fires at the tick on which productivity has been
    below ``threshold`` for exactly ``timeout`` consecutive readings. The run
    must then be broken by a reading at or above the threshold before the unit
    can fire again. Units with no readings are silent.
    """
    if timeout < 1:
        raise ValueError("timeout must be at least one reading")
    if not (0.0 <= threshold <= 1.0):
        raise ValueError("threshold is a productivity ratio in 0..1")

    events: list[AlgedonicEvent] = []
    for path, unit in root.walk():
        series = readings.get(unit.id)
        if not series:
            continue
        run = 0
        armed = True
        for tick, p in enumerate(series):
            if p < threshold:
                run += 1
                if armed and run == timeout:
                    # Escalate from the unit's own system up to the root.
                    events.append(AlgedonicEvent(tick, unit.id, p, tuple(reversed(path))))
                    armed = False
            else:
                run = 0
                armed = True
    events.sort(key=lambda e: (e.tick, e.depth, e.unit_id))
    return events
