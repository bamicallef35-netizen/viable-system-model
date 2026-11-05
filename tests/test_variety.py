import math

import pytest
from hypothesis import given
from hypothesis import strategies as st

from vsm import Amplifier, Attenuator, balance, requisite, variety, variety_of


def test_variety_in_bits() -> None:
    assert variety(1) == 0.0
    assert variety(2) == 1.0
    assert variety(8) == 3.0
    assert math.isclose(variety(10), math.log2(10))


def test_variety_as_count() -> None:
    assert variety(5, bits=False) == 5.0


def test_variety_rejects_empty_state_space() -> None:
    with pytest.raises(ValueError):
        variety(0)


def test_variety_of_counts_distinct_observations() -> None:
    assert variety_of(["a", "b", "a", "c"]) == 3
    assert variety_of([]) == 0


def test_requisite_cases() -> None:
    equal = requisite(3, 3)
    assert equal.is_requisite and equal.residual_outcome_bits == 0 and equal.deficit_bits == 0
    short = requisite(5, 3)
    assert not short.is_requisite and short.deficit_bits == 2 and short.residual_outcome_bits == 2
    spare = requisite(3, 5)
    assert spare.is_requisite and spare.residual_outcome_bits == 0


def test_requisite_rejects_negative_variety() -> None:
    with pytest.raises(ValueError):
        requisite(-1, 2)


@given(st.floats(0, 1e6), st.floats(0, 1e6))
def test_ashby_bound_property(d: float, r: float) -> None:
    res = requisite(d, r)
    assert res.residual_outcome_bits == max(0.0, d - r)
    assert res.deficit_bits == res.residual_outcome_bits
    assert res.is_requisite == (r >= d)


def test_attenuator_and_amplifier_laws() -> None:
    assert Attenuator(0).apply(4.0) == 4.0          # identity
    assert Amplifier(0).apply(4.0) == 4.0
    assert Attenuator(1.5).apply(4.0) == 2.5        # removes variety
    assert Attenuator(9).apply(4.0) == 0.0          # never below zero
    assert Amplifier(2).apply(4.0) == 6.0           # adds variety
    assert Attenuator(1).apply(Attenuator(1).apply(5.0)) == Attenuator(2).apply(5.0)  # composes


def test_transforms_reject_negative_bits() -> None:
    with pytest.raises(ValueError):
        Attenuator(-1)
    with pytest.raises(ValueError):
        Amplifier(-1)


def test_variety_engineering_reaches_balance() -> None:
    # 8 bits of environment against a 6-bit regulator is short by two.
    assert not requisite(8, 6).is_requisite
    # Attenuate the environment by 1.5 and amplify the regulator by 1: balanced.
    res = balance(8, 6, attenuators=[Attenuator(1.5)], amplifiers=[Amplifier(1.0)])
    assert res.is_requisite
    assert res.disturbance_bits == 6.5 and res.regulator_bits == 7.0
