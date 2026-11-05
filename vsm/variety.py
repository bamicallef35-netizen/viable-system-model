"""Ashby's variety and the Law of Requisite Variety.

Variety is the number of distinguishable states of a system, or its
logarithm to the base 2 (Ashby, *An Introduction to Cybernetics*, 1956,
p. 126). The Law of Requisite Variety — "only variety can destroy variety"
(ibid., p. 207) — bounds what a regulator can achieve: the variety of
outcomes can be no smaller than the variety of disturbances less the variety
of the regulator,

    V_O  >=  V_D  -  V_R .

Beer's management restatement is "variety absorbs variety" (*The Heart of
Enterprise*, 1979, p. 286), and his practice of *variety engineering* is to
attenuate the variety a regulator must absorb and amplify the variety of its
response until the two balance.

Everything here is exact arithmetic over state spaces the caller stipulates.
It says nothing about how much variety a real organization or environment
has; estimating that is the hard, unmodelled step.
"""

from __future__ import annotations

import math
from collections.abc import Hashable, Iterable, Sequence
from dataclasses import dataclass


def variety(states: int, *, bits: bool = True) -> float:
    """Variety of a system with ``states`` distinguishable states.

    Returns ``log2(states)`` by default (Ashby's logarithmic measure), or the
    raw count with ``bits=False``. One state has zero variety.
    """
    if states < 1:
        raise ValueError(f"a system has at least one state, got {states}")
    return math.log2(states) if bits else float(states)


def variety_of(elements: Iterable[Hashable]) -> int:
    """Count the distinct elements — the variety of a set of observations."""
    return len(set(elements))


@dataclass(frozen=True)
class RequisiteResult:
    """The outcome of testing a regulator against a disturbance (in bits)."""

    disturbance_bits: float
    regulator_bits: float

    @property
    def is_requisite(self) -> bool:
        """True when the regulator has at least as much variety as the disturbance."""
        return self.regulator_bits >= self.disturbance_bits

    @property
    def deficit_bits(self) -> float:
        """How much variety the regulator is short, zero if none."""
        return max(0.0, self.disturbance_bits - self.regulator_bits)

    @property
    def residual_outcome_bits(self) -> float:
        """Ashby's lower bound on outcome variety, ``max(0, V_D - V_R)``."""
        return max(0.0, self.disturbance_bits - self.regulator_bits)


def requisite(disturbance_bits: float, regulator_bits: float) -> RequisiteResult:
    """Apply the Law of Requisite Variety to a disturbance and a regulator."""
    if disturbance_bits < 0 or regulator_bits < 0:
        raise ValueError("variety in bits cannot be negative")
    return RequisiteResult(disturbance_bits, regulator_bits)


@dataclass(frozen=True)
class Attenuator:
    """Reduces the variety a regulator must absorb, by ``bits``.

    An abstract transform standing for any of Beer's attenuators — a filter,
    a summary, a policy that rules options out. It claims nothing about which
    real mechanism produces the reduction.
    """

    bits: float

    def __post_init__(self) -> None:
        if self.bits < 0:
            raise ValueError("an attenuator removes a non-negative number of bits")

    def apply(self, variety_bits: float) -> float:
        return max(0.0, variety_bits - self.bits)


@dataclass(frozen=True)
class Amplifier:
    """Increases the variety of a regulator's response, by ``bits``.

    An abstract transform standing for any of Beer's amplifiers — delegation,
    tooling, a richer repertoire. Likewise agnostic about mechanism.
    """

    bits: float

    def __post_init__(self) -> None:
        if self.bits < 0:
            raise ValueError("an amplifier adds a non-negative number of bits")

    def apply(self, variety_bits: float) -> float:
        return variety_bits + self.bits


def balance(
    disturbance_bits: float,
    regulator_bits: float,
    attenuators: Sequence[Attenuator] = (),
    amplifiers: Sequence[Amplifier] = (),
) -> RequisiteResult:
    """Beer's variety-engineering loop: attenuate the disturbance, amplify the
    regulator, then test the pair against Ashby's law."""
    d = disturbance_bits
    for a in attenuators:
        d = a.apply(d)
    r = regulator_bits
    for m in amplifiers:
        r = m.apply(r)
    return requisite(d, r)
