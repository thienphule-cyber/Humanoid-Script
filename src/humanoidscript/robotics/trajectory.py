"""
trajectory.py

Phase 5 — Trajectory generation.

Generates a smooth sequence of joint configurations between a
start and end configuration, using simple linear interpolation:

    q(t) = q_start + t * (q_end - q_start),  t in [0, 1]

This is intentionally simple (no velocity/acceleration limits yet)
so the concept of "don't teleport the robot" is demonstrated cleanly.
Velocity/acceleration-constrained trajectories are a natural
extension for a later phase.
"""

import numpy as np

DEFAULT_STEPS = 50


def generate_trajectory(q_start: list, q_end: list, steps: int = DEFAULT_STEPS) -> list:
    """
    Returns a list of `steps` joint configurations (each a list of
    floats) interpolated linearly from q_start to q_end, inclusive
    of both endpoints.
    """
    if steps < 2:
        raise ValueError("steps must be at least 2 (start and end)")

    if len(q_start) != len(q_end):
        raise ValueError("q_start and q_end must have the same number of joints")

    q_start_arr = np.array(q_start, dtype=float)
    q_end_arr = np.array(q_end, dtype=float)

    trajectory = []
    for i in range(steps):
        t = i / (steps - 1)
        q_t = q_start_arr + t * (q_end_arr - q_start_arr)
        trajectory.append(q_t.tolist())

    return trajectory