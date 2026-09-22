"""
test_trajectory.py

Phase 5 unit tests — Trajectory generation.
"""

import pytest
from humanoidscript.robotics.trajectory import generate_trajectory


def test_trajectory_start_end():
    q0 = [0, 0, 0]
    q1 = [1, 0.5, -0.3]

    trajectory = generate_trajectory(q0, q1, steps=10)

    assert trajectory[0] == pytest.approx(q0)
    assert trajectory[-1] == pytest.approx(q1)


def test_trajectory_has_requested_number_of_steps():
    trajectory = generate_trajectory([0, 0, 0], [1, 1, 1], steps=25)
    assert len(trajectory) == 25


def test_trajectory_is_monotonic_for_single_joint():
    """For a single increasing joint, each waypoint should be >= the previous one."""
    trajectory = generate_trajectory([0], [10], steps=5)
    values = [q[0] for q in trajectory]

    assert values == sorted(values)


def test_trajectory_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        generate_trajectory([0, 0], [1, 1, 1])


def test_trajectory_too_few_steps_raises():
    with pytest.raises(ValueError):
        generate_trajectory([0], [1], steps=1)