"""
commands.py

Phase 4 — Executed humanoid command records.

These are lightweight dataclasses representing a command that has
already been executed by the HumanoidRuntime. They exist so tests
(and later, the simulator in Phase 6) can inspect exactly what the
robot did, in order, without re-parsing log strings.
"""

from dataclasses import dataclass


class ExecutedCommand:
    """Base marker class for all executed humanoid commands."""
    pass


@dataclass
class RobotDeclared(ExecutedCommand):
    name: str


@dataclass
class StandExecuted(ExecutedCommand):
    pass


@dataclass
class WalkExecuted(ExecutedCommand):
    direction: str
    distance: float
    unit: str


@dataclass
class TurnExecuted(ExecutedCommand):
    direction: str
    angle: float
    unit: str


@dataclass
class ReachExecuted(ExecutedCommand):
    hand: str
    target: str


@dataclass
class GraspExecuted(ExecutedCommand):
    target: str


@dataclass
class ReleaseExecuted(ExecutedCommand):
    target: str