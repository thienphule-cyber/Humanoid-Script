"""
kinematics.py

Phase 5 — Forward Kinematics (FK).

Computes the end-effector pose (x, y, orientation) of a
HumanoidArm given a joint configuration, using a simple planar
serial-chain formulation:

    theta1 = q0
    theta2 = q0 + q1
    theta3 = q0 + q1 + q2

    x = L1*cos(theta1) + L2*cos(theta2) + L3*cos(theta3)
    y = L1*sin(theta1) + L2*sin(theta2) + L3*sin(theta3)

Joint angles (q) are expected in radians. Use math.radians()
to convert from the degree-based syntax used in HumanoidScript
source programs.
"""

import math
from dataclasses import dataclass

from humanoidscript.robotics.humanoid import HumanoidArm


@dataclass
class EndEffectorPose:
    x: float
    y: float
    orientation: float  # radians


def forward_kinematics(arm: HumanoidArm, q: list) -> EndEffectorPose:
    """
    q: [shoulder_rad, elbow_rad, wrist_rad] joint angles in radians.
    """
    if len(q) != 3:
        raise ValueError("Expected 3 joint angles: [shoulder, elbow, wrist]")

    l1 = arm.link_lengths["shoulder_to_elbow"]
    l2 = arm.link_lengths["elbow_to_wrist"]
    l3 = arm.link_lengths["wrist_to_end_effector"]

    theta1 = q[0]
    theta2 = q[0] + q[1]
    theta3 = q[0] + q[1] + q[2]

    x = l1 * math.cos(theta1) + l2 * math.cos(theta2) + l3 * math.cos(theta3)
    y = l1 * math.sin(theta1) + l2 * math.sin(theta2) + l3 * math.sin(theta3)

    return EndEffectorPose(x=x, y=y, orientation=theta3)


def joint_positions(arm: HumanoidArm, q: list) -> list:
    """
    Returns the (x, y) position of every joint along the chain,
    starting at the shoulder (origin) and ending at the end-effector.
    Useful for collision checking and visualization (Phase 6).
    """
    l1 = arm.link_lengths["shoulder_to_elbow"]
    l2 = arm.link_lengths["elbow_to_wrist"]
    l3 = arm.link_lengths["wrist_to_end_effector"]

    theta1 = q[0]
    theta2 = q[0] + q[1]
    theta3 = q[0] + q[1] + q[2]

    shoulder = (0.0, 0.0)
    elbow = (l1 * math.cos(theta1), l1 * math.sin(theta1))
    wrist = (
        elbow[0] + l2 * math.cos(theta2),
        elbow[1] + l2 * math.sin(theta2),
    )
    end_effector = (
        wrist[0] + l3 * math.cos(theta3),
        wrist[1] + l3 * math.sin(theta3),
    )

    return [shoulder, elbow, wrist, end_effector]