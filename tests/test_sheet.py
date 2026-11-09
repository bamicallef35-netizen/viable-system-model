"""The sheet is drawn from the model objects, deterministically."""

from __future__ import annotations

import re

from vsm import examples
from vsm.algedonic import propagate
from vsm.sheet import sheet


def _factory_sheet() -> str:
    root = examples.factory()
    events = propagate(root, examples.factory_readings(), threshold=0.6, timeout=3)
    return sheet(root, examples.factory_requisite(), events, threshold=0.6, timeout=3)


def test_sheet_is_one_svg_with_the_scenario_block() -> None:
    svg = _factory_sheet()
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    for key in ("project", "programme", "area", "procedure", "record", "requisite variety"):
        assert key in svg


def test_every_unit_and_system_is_named_on_the_sheet() -> None:
    svg = _factory_sheet()
    root = examples.factory()
    for _, u in root.walk():
        assert u.id in svg
    for name in ("Company", "Plant North", "Plant South"):
        assert name in svg


def test_alarms_and_the_variety_shortfall_are_drawn_in_the_accent() -> None:
    svg = _factory_sheet()
    assert "alarm, tick" in svg and "line-S2" in svg
    assert "short by 2 bits" in svg
    assert svg.count('stroke="#0000ee"') >= 1


def test_a_missing_function_is_marked() -> None:
    svg = sheet(examples.imbalanced())
    assert "!S4" in svg and "structurally viable: no" in svg


def test_deterministic_and_well_formed_numbers() -> None:
    assert _factory_sheet() == _factory_sheet()
    assert not re.search(r"\d\.\d+\.\d", _factory_sheet())
    assert "nan" not in _factory_sheet().lower()
