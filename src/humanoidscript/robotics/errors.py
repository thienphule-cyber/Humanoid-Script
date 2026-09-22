"""
errors.py

Phase 4/5/6 — Robotics-domain errors.

Phase 4 errors relate to the humanoid DSL command state machine
(reach/grasp/release). Phase 5 errors relate to the robotics
engine itself: joint limits, inverse kinematics convergence, and
collision/reachability checks. Phase 6 adds balance checking
during simulation.
"""


class HumanoidStateError(Exception):
    """Raised when a command is invalid given the robot's current state."""
    pass


class InvalidHandError(Exception):
    """Raised when a command references a hand that does not exist."""
    pass


class JointLimitError(Exception):
    """Raised when a joint angle falls outside its allowed range."""
    pass


class UnreachableTargetError(Exception):
    """Raised when a target position is outside the arm's total reach."""
    pass


class IKConvergenceError(Exception):
    """Raised when the inverse kinematics solver fails to converge."""
    pass


class CollisionError(Exception):
    """Raised when a trajectory would bring the end-effector into an obstacle."""
    pass


class BalanceViolationError(Exception):
    """Raised when the robot's center of mass falls outside its support polygon."""
    pass