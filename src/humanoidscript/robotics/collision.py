"""
collision.py

Phase 5 — Simplified collision checking.

Models obstacles as spheres (circles, in this planar arm's case)
with a center and radius. A trajectory is considered to collide
if the end-effector's position at any waypoint falls inside an
obstacle's radius (plus an optional safety margin).

This is intentionally simple: full self-collision (arm vs torso)
and swept-volume collision (checking the whole link, not just the
end-effector) are natural extensions for later refinement.
"""

from dataclasses import dataclass

from humanoidscript.robotics.humanoid import HumanoidArm
from humanoidscript.robotics.kinematics import forward_kinematics
from humanoidscript.robotics.errors import CollisionError


@dataclass
class Obstacle:
    x: float
    y: float
    radius: float


def check_point_collision(x: float, y: float, obstacle: Obstacle, margin: float = 0.0) -> bool:
    """Returns True if point (x, y) is inside obstacle's radius + margin."""
    distance = ((x - obstacle.x) ** 2 + (y - obstacle.y) ** 2) ** 0.5
    return distance <= (obstacle.radius + margin)


def check_trajectory_collision(
    arm: HumanoidArm,
    trajectory: list,
    obstacles: list,
    margin: float = 0.0,
) -> None:
    """
    Checks every waypoint of a joint-space trajectory for collision
    between the end-effector and any given obstacle.

    Raises:
        CollisionError: if any waypoint's end-effector position
        falls inside an obstacle.

    Returns None (silently) if the trajectory is collision-free.
    """
    for step_index, q in enumerate(trajectory):
        pose = forward_kinematics(arm, q)

        for obstacle in obstacles:
            if check_point_collision(pose.x, pose.y, obstacle, margin):
                raise CollisionError(
                    f"Collision detected at trajectory step {step_index}: "
                    f"end-effector at ({pose.x:.3f}, {pose.y:.3f}) "
                    f"is inside obstacle at ({obstacle.x}, {obstacle.y}) "
                    f"with radius {obstacle.radius}"
                )