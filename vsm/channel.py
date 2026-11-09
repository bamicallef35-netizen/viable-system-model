"""Channels and transducers, after Beer's principles of organization.

Beer's first principles (*The Heart of Enterprise*, 1979) govern the
plumbing between parts of a viable system: a channel carrying information
between two parts must have a capacity at least equal to the variety of the
subsystem it serves, and wherever information crosses a boundary and is
re-coded, the transducer must command at least the channel's variety. This
module checks those two inequalities over stipulated bit values. It does not
model timing, noise or coding — only capacity.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Channel:
    """A channel with a fixed capacity, in bits per message."""

    capacity_bits: float

    def __post_init__(self) -> None:
        if self.capacity_bits < 0:
            raise ValueError("capacity cannot be negative")

    def transmit(self, message_bits: float) -> Transmission:
        """Transmit a message; saturated when it exceeds capacity."""
        if message_bits < 0:
            raise ValueError("a message cannot carry negative variety")
        return Transmission(message_bits, self.capacity_bits)


@dataclass(frozen=True)
class Transmission:
    message_bits: float
    capacity_bits: float

    @property
    def saturated(self) -> bool:
        return self.message_bits > self.capacity_bits

    @property
    def lost_bits(self) -> float:
        return max(0.0, self.message_bits - self.capacity_bits)


def channel_violations(
    served_variety_bits: float,
    channel_capacity_bits: float,
    transducer_variety_bits: float,
) -> list[str]:
    """Return the violated principles, as plain sentences; empty means sound.

    Checks (1) channel capacity must not fall below the variety of the
    subsystem it serves, and (2) transducer variety must not fall below the
    channel's capacity.
    """
    problems: list[str] = []
    if channel_capacity_bits < served_variety_bits:
        problems.append(
            f"channel capacity {channel_capacity_bits:g} bits is below the "
            f"{served_variety_bits:g} bits of variety it must carry"
        )
    if transducer_variety_bits < channel_capacity_bits:
        problems.append(
            f"transducer variety {transducer_variety_bits:g} bits is below the "
            f"channel capacity of {channel_capacity_bits:g} bits"
        )
    return problems
