"""
test_collision.py

Phase 5 unit tests — Collision checking.
"""

import pytest
from humanoidscript.robotics.humanoid import HumanoidArm
from humanoidscript.robotics.trajectory import generate_trajectory
from humanoidscript.robotics.collision import Obstacle, check_trajectory_collision, check_point_collision
from humanoidscript.robotics.errors import CollisionError


def test_point_collision_detects_inside_obstacle():
    obstacle = Obstacle(x=0.5, y=0.0, radius=0.1)
    assert check_point_collision(0.52, 0.0, obstacle) is True


def test_point_collision_ignores_far_point():
    obstacle = Obstacle(x=0.5, y=0.0, radius=0.1)
    assert check_point_collision(0.0, 0.0, obstacle) is False


def test_trajectory_collision_free_passes_silently():
    arm = HumanoidArm()
    trajectory = generate_trajectory([0, 0, 0], [0.2, 0, 0], steps=5)
    obstacle = Obstacle(x=-1.0, y=-1.0, radius=0.05)  # far from the arm's path

    # Should not raise
    check_trajectory_collision(arm, trajectory, [obstacle])


def test_trajectory_collision_detected_raises():
    arm = HumanoidArm()
    # End-effector at q=[0,0,0] sits at (0.65, 0) — place an obstacle there
    trajectory = generate_trajectory([0, 0, 0], [0, 0, 0], steps=2)
    obstacle = Obstacle(x=0.65, y=0.0, radius=0.05)

    with pytest.raises(CollisionError):
        check_trajectory_collision(arm, trajectory, [obstacle])


def test_trajectory_collision_respects_margin():
    arm = HumanoidArm()
    trajectory = generate_trajectory([0, 0, 0], [0, 0, 0], steps=2)
    # Obstacle just outside the raw radius, but within radius + margin
    obstacle = Obstacle(x=0.75, y=0.0, radius=0.05)

    with pytest.raises(CollisionError):
        check_trajectory_collision(arm, trajectory, [obstacle], margin=0.1)