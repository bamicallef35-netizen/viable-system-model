"""vsm — an executable, cited model of Stafford Beer's Viable System Model,
with Ashby's variety mathematics done exactly.

See README.md for what this can and cannot prove.
"""

from .algedonic import AlgedonicEvent, propagate
from .channel import Channel, Transmission, channel_violations
from .system import Metrics, System1, ViableSystem
from .variety import (
    Amplifier,
    Attenuator,
    RequisiteResult,
    balance,
    requisite,
    variety,
    variety_of,
)

__version__ = "0.1.0"

__all__ = [
    "AlgedonicEvent",
    "Amplifier",
    "Attenuator",
    "Channel",
    "Metrics",
    "RequisiteResult",
    "System1",
    "Transmission",
    "ViableSystem",
    "balance",
    "channel_violations",
    "propagate",
    "requisite",
    "variety",
    "variety_of",
]
