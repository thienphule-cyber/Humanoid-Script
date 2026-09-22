"""
ik.py

Phase 5/7 — Inverse Kinematics (IK).

Solves for a joint configuration [shoulder, elbow, wrist] (radians)
that brings the end-effector to a target (x, y) position, using an
iterative damped pseudo-inverse Jacobian method with a null-space
secondary objective and hard joint-limit clamping. Uses multi-start
(several initial guesses, sampled within the joint limits) since
clamping can trap a single attempt at a joint-limit boundary even
when the target is reachable from a different starting pose.
"""

import math
import numpy as np

from humanoidscript.robotics.humanoid import HumanoidArm, JOINT_NAMES
from humanoidscript.robotics.kinematics import forward_kinematics
from humanoidscript.robotics.errors import UnreachableTargetError, IKConvergenceError

DEFAULT_TOLERANCE = 1e-4
DEFAULT_MAX_ITERATIONS = 300
DEFAULT_STEP_SIZE = 0.5
DEFAULT_DAMPING = 0.01
DEFAULT_RANDOM_RESTARTS = 40

# Fixed seed so IK results are reproducible across runs (important for tests).
_RNG = np.random.default_rng(seed=42)


def _jacobian(arm: HumanoidArm, q: list) -> np.ndarray:
    l1 = arm.link_lengths["shoulder_to_elbow"]
    l2 = arm.link_lengths["elbow_to_wrist"]
    l3 = arm.link_lengths["wrist_to_end_effector"]

    theta1 = q[0]
    theta2 = q[0] + q[1]
    theta3 = q[0] + q[1] + q[2]

    dx_dq0 = -l1 * math.sin(theta1) - l2 * math.sin(theta2) - l3 * math.sin(theta3)
    dx_dq1 = -l2 * math.sin(theta2) - l3 * math.sin(theta3)
    dx_dq2 = -l3 * math.sin(theta3)

    dy_dq0 = l1 * math.cos(theta1) + l2 * math.cos(theta2) + l3 * math.cos(theta3)
    dy_dq1 = l2 * math.cos(theta2) + l3 * math.cos(theta3)
    dy_dq2 = l3 * math.cos(theta3)

    return np.array([
        [dx_dq0, dx_dq1, dx_dq2],
        [dy_dq0, dy_dq1, dy_dq2],
    ])


def _clamp_to_joint_limits(arm: HumanoidArm, q: np.ndarray) -> np.ndarray:
    clamped = q.copy()
    for i, joint_name in enumerate(JOINT_NAMES):
        min_deg, max_deg = arm.joint_limits[joint_name]
        min_rad, max_rad = math.radians(min_deg), math.radians(max_deg)
        clamped[i] = np.clip(clamped[i], min_rad, max_rad)
    return clamped


def _random_initial_guess(arm: HumanoidArm) -> list:
    """Samples a random joint configuration uniformly within the
    arm's joint limits, so multi-start attempts actually cover the
    whole valid configuration space rather than a few fixed guesses."""
    q = []
    for joint_name in JOINT_NAMES:
        min_deg, max_deg = arm.joint_limits[joint_name]
        angle_deg = _RNG.uniform(min_deg, max_deg)
        q.append(math.radians(angle_deg))
    return q


def _solve_single_attempt(
    arm: HumanoidArm,
    target: np.ndarray,
    q0: list,
    tolerance: float,
    max_iterations: int,
    step_size: float,
    damping: float,
    null_space_gain: float,
):
    """
    Runs one damped-Jacobian IK attempt from starting configuration q0.
    Returns the solved [q0, q1, q2] list on success, or None if this
    attempt did not converge within max_iterations.

    Uses active-set joint-limit handling: if a joint is sitting at its
    limit and the computed step would push it further out of bounds,
    that joint is frozen for this iteration instead of being silently
    clamped after the fact. Naive post-hoc clamping wastes iterations
    by repeatedly trying to push the same joint past its boundary;
    freezing it lets the remaining iterations make real progress on
    the other joints.
    """
    q = _clamp_to_joint_limits(arm, np.array(q0, dtype=float))
    home_bias = np.zeros(3)

    for _ in range(max_iterations):
        pose = forward_kinematics(arm, q.tolist())
        current = np.array([pose.x, pose.y])
        error = target - current

        if np.linalg.norm(error) < tolerance:
            return q.tolist()

        jacobian = _jacobian(arm, q.tolist())

        jjt = jacobian @ jacobian.T
        damped = jjt + (damping ** 2) * np.eye(2)
        j_pinv_damped = jacobian.T @ np.linalg.inv(damped)
        primary = j_pinv_damped @ error

        j_pinv_exact = np.linalg.pinv(jacobian)
        null_space_projector = np.eye(3) - j_pinv_exact @ jacobian
        secondary = null_space_projector @ (null_space_gain * (home_bias - q))

        delta_q = primary + secondary

        # Active-set freeze: stop a joint that's already at its limit
        # from being pushed further out, so the step doesn't just get
        # wasted on a direction that clamping will undo anyway.
        for i, joint_name in enumerate(JOINT_NAMES):
            min_deg, max_deg = arm.joint_limits[joint_name]
            min_rad, max_rad = math.radians(min_deg), math.radians(max_deg)
            at_lower_limit = q[i] <= min_rad + 1e-9 and delta_q[i] < 0
            at_upper_limit = q[i] >= max_rad - 1e-9 and delta_q[i] > 0
            if at_lower_limit or at_upper_limit:
                delta_q[i] = 0.0

        q = q + step_size * delta_q
        q = _clamp_to_joint_limits(arm, q)

    return None  # did not converge from this starting point


def inverse_kinematics(
    arm: HumanoidArm,
    target_x: float,
    target_y: float,
    initial_guess: list = None,
    tolerance: float = DEFAULT_TOLERANCE,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    step_size: float = DEFAULT_STEP_SIZE,
    damping: float = DEFAULT_DAMPING,
    null_space_gain: float = 0.3,
    random_restarts: int = DEFAULT_RANDOM_RESTARTS,
) -> list:
    """
    Returns [shoulder_rad, elbow_rad, wrist_rad] that place the
    end-effector at (target_x, target_y), within `tolerance` meters,
    while always respecting the arm's joint limits.

    Tries `initial_guess` first (if given), then `random_restarts`
    configurations sampled uniformly within the joint limits, since
    hard joint-limit clamping can trap a single attempt at a boundary
    even when the target is reachable from a different starting pose.
    Random multi-start covers the valid configuration space far more
    reliably than a small fixed list of starting guesses.

    Raises:
        UnreachableTargetError: target is farther than the arm's total reach.
        IKConvergenceError: no starting attempt converged within
            max_iterations.
    """
    distance_to_target = math.hypot(target_x, target_y)
    if distance_to_target > arm.total_reach:
        raise UnreachableTargetError(
            f"Target ({target_x}, {target_y}) is {distance_to_target:.3f}m away, "
            f"which exceeds the arm's total reach of {arm.total_reach:.3f}m"
        )

    target = np.array([target_x, target_y])

    attempts = []
    if initial_guess is not None:
        attempts.append(initial_guess)
    attempts.extend(_random_initial_guess(arm) for _ in range(random_restarts))

    for q0 in attempts:
        result = _solve_single_attempt(
            arm, target, q0, tolerance, max_iterations, step_size, damping, null_space_gain
        )
        if result is not None:
            return result

    raise IKConvergenceError(
        f"IK did not converge to target ({target_x}, {target_y}) "
        f"after trying {len(attempts)} starting configurations "
        f"(joint limits may make this target unreachable in a valid pose)"
    )