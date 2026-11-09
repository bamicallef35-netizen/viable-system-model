import pytest
from hypothesis import given
from hypothesis import strategies as st

from vsm import Metrics, System1, ViableSystem, examples, propagate


def _root() -> ViableSystem:
    return examples.factory()


def test_steady_performance_raises_no_alarm() -> None:
    readings = {"line-N1": [0.9] * 10}
    assert propagate(_root(), readings, threshold=0.6, timeout=3) == []


def test_brief_dip_shorter_than_timeout_is_tolerated() -> None:
    readings = {"line-N1": [0.9, 0.9, 0.4, 0.4, 0.9, 0.9]}      # two low readings, timeout three
    assert propagate(_root(), readings, threshold=0.6, timeout=3) == []


def test_sustained_dip_fires_exactly_once_with_the_escalation_route() -> None:
    readings = {"line-S2": [0.9, 0.5, 0.5, 0.5, 0.5, 0.5]}
    events = propagate(_root(), readings, threshold=0.6, timeout=3)
    assert len(events) == 1
    e = events[0]
    assert e.unit_id == "line-S2"
    assert e.tick == 3                                           # the third consecutive low reading
    assert e.productivity == 0.5
    assert e.path == ("Plant South", "Company")                  # up the recursion, bypassing System 2
    assert e.depth == 2


def test_recovery_then_relapse_fires_again() -> None:
    readings = {"line-S2": [0.5, 0.5, 0.5, 0.9, 0.5, 0.5, 0.5]}
    events = propagate(_root(), readings, threshold=0.6, timeout=3)
    assert [e.tick for e in events] == [2, 6]


def test_deep_leaf_escalates_all_the_way_to_the_top() -> None:
    leaf = ViableSystem("Cell", operations=[System1("c1", Metrics(1, 2, 3))])
    mid = ViableSystem("Team", operations=[System1("t1", Metrics(1, 2, 3), subsystem=leaf)])
    top = ViableSystem("Org", operations=[System1("o1", Metrics(1, 2, 3), subsystem=mid)])
    events = propagate(top, {"c1": [0.1, 0.1]}, threshold=0.5, timeout=2)
    assert len(events) == 1
    assert events[0].path == ("Cell", "Team", "Org")


def test_bundled_readings_flag_only_the_failing_line() -> None:
    events = propagate(_root(), examples.factory_readings(), threshold=0.6, timeout=3)
    assert [e.unit_id for e in events] == ["line-S2"]
    assert events[0].tick == 4


def test_events_are_ordered_by_tick_then_depth_then_id() -> None:
    readings = {"line-S2": [0.1, 0.1], "line-N1": [0.1, 0.1], "plant-north": [0.1, 0.1]}
    events = propagate(_root(), readings, threshold=0.5, timeout=2)
    assert [(e.tick, e.depth, e.unit_id) for e in events] == [
        (1, 1, "plant-north"),
        (1, 2, "line-N1"),
        (1, 2, "line-S2"),
    ]


def test_invalid_parameters_are_rejected() -> None:
    with pytest.raises(ValueError):
        propagate(_root(), {}, threshold=0.6, timeout=0)
    with pytest.raises(ValueError):
        propagate(_root(), {}, threshold=1.5, timeout=1)


def _expected_alarms(series: list[float], threshold: float, timeout: int) -> int:
    """Independent reference: count maximal runs of low readings of length >= timeout."""
    count, run = 0, 0
    for p in series:
        run = run + 1 if p < threshold else 0
        if run == timeout:
            count += 1
    return count


@given(
    st.lists(st.floats(0, 1, allow_nan=False), min_size=1, max_size=40),
    st.floats(0.05, 0.95),
    st.integers(1, 6),
)
def test_alarm_count_matches_run_structure(series: list[float], threshold: float, timeout: int) -> None:
    events = propagate(_root(), {"line-N1": series}, threshold=threshold, timeout=timeout)
    assert len(events) == _expected_alarms(series, threshold, timeout)
    assert all(e.unit_id == "line-N1" and e.productivity < threshold for e in events)
