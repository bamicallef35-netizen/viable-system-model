"""Bundled example models, used by ``python -m vsm demo`` and the tests.

The numbers are illustrative. They stipulate state spaces; they do not
measure a real company.
"""

from __future__ import annotations

from .system import Metrics, System1, ViableSystem
from .variety import Amplifier, Attenuator, RequisiteResult, balance, requisite, variety


def factory() -> ViableSystem:
    """A three-level recursion: Company -> Plant -> Line, all functions present."""
    north = ViableSystem(
        "Plant North",
        operations=[
            System1("line-N1", Metrics(90, 100, 120)),
            System1("line-N2", Metrics(85, 100, 120)),
        ],
    )
    south = ViableSystem(
        "Plant South",
        operations=[
            System1("line-S1", Metrics(95, 100, 110)),
            System1("line-S2", Metrics(50, 100, 120)),
        ],
    )
    return ViableSystem(
        "Company",
        operations=[
            System1("plant-north", Metrics(175, 200, 240), subsystem=north),
            System1("plant-south", Metrics(145, 200, 230), subsystem=south),
        ],
    )


def factory_readings() -> dict[str, list[float]]:
    """Productivity per tick for the leaf lines; line-S2 dips and stays down."""
    steady = [0.90, 0.91, 0.90, 0.89, 0.90, 0.91, 0.90, 0.90]
    return {
        "line-N1": list(steady),
        "line-N2": [0.85, 0.84, 0.86, 0.85, 0.85, 0.84, 0.86, 0.85],
        "line-S1": [0.95, 0.94, 0.95, 0.96, 0.95, 0.94, 0.95, 0.95],
        "line-S2": [0.90, 0.88, 0.50, 0.48, 0.47, 0.52, 0.90, 0.91],
    }


def factory_requisite() -> list[tuple[str, RequisiteResult]]:
    """Each plant's regulator tested against the variety of its environment."""
    return [
        ("Plant North", requisite(variety(64), variety(128))),   # 6 vs 7 bits: fine
        ("Plant South", requisite(variety(256), variety(64))),   # 8 vs 6 bits: short by 2
    ]


def variety_engineering() -> tuple[RequisiteResult, RequisiteResult]:
    """Beer's loop on Plant South: attenuate the environment, amplify the
    response, and the pair comes into balance."""
    before = requisite(variety(256), variety(64))
    after = balance(
        variety(256),
        variety(64),
        attenuators=[Attenuator(1.5)],   # summary reporting filters the environment
        amplifiers=[Amplifier(1.0)],     # delegation widens the regulator's repertoire
    )
    return before, after


def imbalanced() -> ViableSystem:
    """A company whose southern plant has no System 4 — structurally not viable."""
    south = ViableSystem(
        "Plant South",
        operations=[System1("line-S1", Metrics(95, 100, 110))],
        s4=False,
    )
    return ViableSystem(
        "Company",
        operations=[System1("plant-south", Metrics(95, 100, 110), subsystem=south)],
    )
