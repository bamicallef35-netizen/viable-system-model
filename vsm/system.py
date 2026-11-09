"""The Viable System Model as a structure: Systems 1–5 and recursion.

Beer's model (*Brain of the Firm*, 1972; *The Heart of Enterprise*, 1979;
*Diagnosing the System for Organizations*, 1985) says any viable
organization has five necessary functions:

  System 1   the operational units that do the work;
  System 2   coordination between them, damping oscillation;
  System 3   internal regulation, here-and-now, with
  System 3*  a sporadic audit channel straight into System 1;
  System 4   intelligence: the outside and the future;
  System 5   policy and identity, holding the 3/4 balance.

and that every System 1 unit is itself a viable system with its own five
functions — Beer's Recursive System Theorem: any viable system contains,
and is contained in, a viable system.

This module encodes that structure and checks it. ``is_structurally_viable``
asks only whether the named functions are present at every level of the
recursion. It does not — cannot — tell you whether a real organization is
viable; the model is a diagnostic lens, not a predictive theory.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Metrics:
    """Beer's triple vector for a System 1 unit.

    actuality    what it is doing now, with current resources;
    capability   what it could do now, with current resources, if it tried;
    potentiality what it could do if resources were developed.

    The three derived ratios are given per Beer; verify the exact wording
    against *Brain of the Firm* before quoting it as his.
    """

    actuality: float
    capability: float
    potentiality: float

    def __post_init__(self) -> None:
        for name, v in (
            ("actuality", self.actuality),
            ("capability", self.capability),
            ("potentiality", self.potentiality),
        ):
            if v <= 0:
                raise ValueError(f"{name} must be positive, got {v}")
        if not (self.actuality <= self.capability <= self.potentiality):
            raise ValueError(
                "expected actuality <= capability <= potentiality, got "
                f"{self.actuality} <= {self.capability} <= {self.potentiality}"
            )

    @property
    def productivity(self) -> float:
        return self.actuality / self.capability

    @property
    def latency(self) -> float:
        return self.capability / self.potentiality

    @property
    def performance(self) -> float:
        return self.actuality / self.potentiality


@dataclass
class System1:
    """An operational unit. If it has a ``subsystem`` it is itself viable."""

    id: str
    metrics: Metrics
    subsystem: ViableSystem | None = None


@dataclass
class ViableSystem:
    """A viable system: its operations plus the four meta-functions."""

    name: str
    operations: list[System1] = field(default_factory=list)
    s2: bool = True
    s3: bool = True
    s3_star: bool = True
    s4: bool = True
    s5: bool = True

    def missing_functions(self) -> list[str]:
        """Which of 2, 3, 3*, 4, 5 are absent at this level (1 needs units)."""
        missing: list[str] = []
        if not self.operations:
            missing.append("System 1 (no operational units)")
        for flag, label in (
            (self.s2, "System 2"),
            (self.s3, "System 3"),
            (self.s3_star, "System 3*"),
            (self.s4, "System 4"),
            (self.s5, "System 5"),
        ):
            if not flag:
                missing.append(label)
        return missing

    def is_structurally_viable(self) -> bool:
        """All five functions present here and in every nested viable system."""
        if self.missing_functions():
            return False
        return all(
            u.subsystem is None or u.subsystem.is_structurally_viable()
            for u in self.operations
        )

    def walk(self) -> Iterator[tuple[tuple[str, ...], System1]]:
        """Yield every System 1 unit with the path of system names above it,
        depth-first, in declaration order."""
        yield from self._walk((self.name,))

    def _walk(self, path: tuple[str, ...]) -> Iterator[tuple[tuple[str, ...], System1]]:
        for u in self.operations:
            yield path, u
            if u.subsystem is not None:
                yield from u.subsystem._walk(path + (u.subsystem.name,))

    def depth(self) -> int:
        """Levels of recursion below this system (0 if no unit nests one)."""
        return max(
            (1 + u.subsystem.depth() for u in self.operations if u.subsystem is not None),
            default=0,
        )

    def find(self, unit_id: str) -> tuple[tuple[str, ...], System1] | None:
        for path, u in self.walk():
            if u.id == unit_id:
                return path, u
        return None
