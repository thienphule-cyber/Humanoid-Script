"""
balance.py

Phase 6 — Simplified balance checking.

A full whole-body balance controller is out of scope for this
project. Instead, this module demonstrates the underlying concept
with a simplified model:

    Center of Mass (COM)
           |
    Support Polygon (a fixed horizontal range on the ground,
                      representing the footprint between the feet)
           |
    Stable if COM's x-coordinate falls inside that range.

The center of mass here is the (unweighted, unless masses are
given) average position of the arm's joints — a simplification
standing in for a full multi-link body COM calculation.
"""

from dataclasses import dataclass
from typing import Optional

from humanoidscript.robotics.errors import BalanceViolationError


@dataclass
class SupportPolygon:
    """A simplified 1D support base: the horizontal range the
    robot's center of mass must stay within to remain stable."""
    min_x: float
    max_x: float

    def contains(self, x: float) -> bool:
        return self.min_x <= x <= self.max_x


def compute_center_of_mass(positions: list, masses: Optional[list] = None) -> tuple:
    """
    positions: list of (x, y) tuples, e.g. from robotics.kinematics.joint_positions.
    masses: optional list of per-joint masses (same length as positions).
            If omitted, all joints are weighted equally.

    Returns (com_x, com_y).
    """
    if len(positions) == 0:
        raise ValueError("Cannot compute center of mass with no positions")

    if masses is None:
        masses = [1.0] * len(positions)

    if len(masses) != len(positions):
        raise ValueError("masses must be the same length as positions")

    total_mass = sum(masses)
    if total_mass == 0:
        raise ValueError("Total mass must be greater than zero")

    com_x = sum(p[0] * m for p, m in zip(positions, masses)) / total_mass
    com_y = sum(p[1] * m for p, m in zip(positions, masses)) / total_mass

    return (com_x, com_y)


def check_balance(positions: list, support: SupportPolygon, masses: Optional[list] = None) -> None:
    """
    Raises BalanceViolationError if the center of mass computed from
    `positions` falls outside `support`. Returns None (silently) if stable.
    """
    com_x, _ = compute_center_of_mass(positions, masses)

    if not support.contains(com_x):
        raise BalanceViolationError(
            f"Balance violation: center of mass x={com_x:.3f} is outside "
            f"support polygon [{support.min_x}, {support.max_x}]"
        )