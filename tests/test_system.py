import pytest

from vsm import Metrics, System1, ViableSystem, examples


def test_metrics_ratios() -> None:
    m = Metrics(actuality=50, capability=100, potentiality=200)
    assert m.productivity == 0.5
    assert m.latency == 0.5
    assert m.performance == 0.25


def test_metrics_must_be_positive_and_ordered() -> None:
    with pytest.raises(ValueError):
        Metrics(0, 1, 2)
    with pytest.raises(ValueError):
        Metrics(5, 4, 6)       # actuality above capability
    with pytest.raises(ValueError):
        Metrics(1, 5, 4)       # capability above potentiality


def test_factory_is_structurally_viable_at_every_level() -> None:
    root = examples.factory()
    assert root.missing_functions() == []
    assert root.is_structurally_viable()
    for _, unit in root.walk():
        if unit.subsystem is not None:
            assert unit.subsystem.is_structurally_viable()   # the recursion theorem, checked


def test_depth_and_walk_paths() -> None:
    root = examples.factory()
    assert root.depth() == 1
    leaves = [(path, u.id) for path, u in root.walk()]
    assert leaves[0] == (("Company",), "plant-north")
    assert (("Company", "Plant North"), "line-N1") in leaves
    assert (("Company", "Plant South"), "line-S2") in leaves
    assert len(leaves) == 6


def test_find_returns_path_and_unit() -> None:
    found = examples.factory().find("line-S2")
    assert found is not None
    path, unit = found
    assert path == ("Company", "Plant South") and unit.id == "line-S2"
    assert examples.factory().find("nope") is None


def test_missing_function_breaks_viability() -> None:
    broken = examples.imbalanced()
    assert broken.missing_functions() == []                 # the top level is fine
    assert not broken.is_structurally_viable()              # a nested level is not
    sub = broken.operations[0].subsystem
    assert sub is not None and sub.missing_functions() == ["System 4"]


def test_empty_operations_is_not_viable() -> None:
    assert "System 1 (no operational units)" in ViableSystem("Shell").missing_functions()
    assert not ViableSystem("Shell").is_structurally_viable()


def test_nested_three_levels() -> None:
    leaf = ViableSystem("Cell", operations=[System1("c1", Metrics(1, 2, 3))])
    mid = ViableSystem("Team", operations=[System1("t1", Metrics(1, 2, 3), subsystem=leaf)])
    top = ViableSystem("Org", operations=[System1("o1", Metrics(1, 2, 3), subsystem=mid)])
    assert top.depth() == 2
    assert top.is_structurally_viable()
    found = top.find("c1")
    assert found is not None and found[0] == ("Org", "Team", "Cell")
