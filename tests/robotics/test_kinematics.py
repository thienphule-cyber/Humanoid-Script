"""
test_kinematics.py

Phase 5 unit tests — Forward Kinematics.
"""

import math
import pytest
from humanoidscript.robotics.humanoid import HumanoidArm
from humanoidscript.robotics.kinematics import forward_kinematics, joint_positions


def test_forward_kinematics_zero_configuration():
    """With all joints at 0 rad, the arm points straight along +x."""
    arm = HumanoidArm()
    pose = forward_kinematics(arm, [0, 0, 0])

    expected_x = sum(arm.link_lengths.values())

    assert pose.x == pytest.approx(expected_x, abs=1e-6)
    assert pose.y == pytest.approx(0.0, abs=1e-6)
    assert pose.orientation == pytest.approx(0.0, abs=1e-6)


def test_forward_kinematics_shoulder_at_90_degrees():
    """With shoulder at 90deg and elbow/wrist straight, arm points along +y."""
    arm = HumanoidArm()
    q = [math.radians(90), 0, 0]
    pose = forward_kinematics(arm, q)

    expected_y = sum(arm.link_lengths.values())

    assert pose.x == pytest.approx(0.0, abs=1e-6)
    assert pose.y == pytest.approx(expected_y, abs=1e-6)


def test_forward_kinematics_wrong_joint_count_raises():
    arm = HumanoidArm()
    with pytest.raises(ValueError):
        forward_kinematics(arm, [0, 0])  # missing wrist angle


def test_joint_positions_returns_four_points():
    arm = HumanoidArm()
    positions = joint_positions(arm, [0, 0, 0])

    assert len(positions) == 4  # shoulder, elbow, wrist, end-effector
    assert positions[0] == pytest.approx((0.0, 0.0))


def test_joint_positions_end_effector_matches_fk():
    arm = HumanoidArm()
    q = [math.radians(30), math.radians(-20), math.radians(10)]

    pose = forward_kinematics(arm, q)
    positions = joint_positions(arm, q)
    end_effector = positions[-1]

    assert end_effector[0] == pytest.approx(pose.x, abs=1e-6)
    assert end_effector[1] == pytest.approx(pose.y, abs=1e-6)