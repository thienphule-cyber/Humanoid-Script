"""
test_ik.py

Phase 5 unit tests — Inverse Kinematics.
"""

import pytest
from humanoidscript.robotics.humanoid import HumanoidArm
from humanoidscript.robotics.kinematics import forward_kinematics
from humanoidscript.robotics.ik import inverse_kinematics
from humanoidscript.robotics.errors import UnreachableTargetError, IKConvergenceError


def test_ik_converges_to_reachable_target():
    arm = HumanoidArm()
    target_x, target_y = 0.4, 0.2

    q = inverse_kinematics(arm, target_x, target_y)
    pose = forward_kinematics(arm, q)

    assert pose.x == pytest.approx(target_x, abs=1e-3)
    assert pose.y == pytest.approx(target_y, abs=1e-3)


def test_ik_round_trip_multiple_targets():
    """For several reachable targets, FK(IK(target)) should match the target."""
    arm = HumanoidArm()
    targets = [(0.3, 0.1), (0.4, 0.1), (0.5, 0.0)]

    for target_x, target_y in targets:
        q = inverse_kinematics(arm, target_x, target_y)
        pose = forward_kinematics(arm, q)

        assert pose.x == pytest.approx(target_x, abs=1e-3)
        assert pose.y == pytest.approx(target_y, abs=1e-3)


def test_ik_unreachable_target_raises():
    arm = HumanoidArm()
    far_away = arm.total_reach + 1.0

    with pytest.raises(UnreachableTargetError):
        inverse_kinematics(arm, far_away, 0)


def test_ik_returns_three_joint_angles():
    arm = HumanoidArm()
    q = inverse_kinematics(arm, 0.3, 0.1)
    assert len(q) == 3