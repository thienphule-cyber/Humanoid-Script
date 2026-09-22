"""
test_humanoid.py

Phase 5 unit tests — HumanoidArm model & joint limits.
"""

import pytest
from humanoidscript.robotics.humanoid import HumanoidArm
from humanoidscript.robotics.errors import JointLimitError


def test_default_total_reach():
    arm = HumanoidArm()
    expected = 0.30 + 0.25 + 0.10
    assert arm.total_reach == pytest.approx(expected)


def test_valid_joint_angle_does_not_raise():
    arm = HumanoidArm()
    arm.validate_joint_limits("shoulder", 45)  # within -90..150


def test_joint_limit_violation_raises():
    arm = HumanoidArm()
    with pytest.raises(JointLimitError):
        arm.validate_joint_limits("elbow", 180)  # elbow max is 120


def test_joint_limit_error_message_includes_range():
    arm = HumanoidArm()
    with pytest.raises(JointLimitError, match="Allowed range: -10.0deg to 120.0deg"):
        arm.validate_joint_limits("elbow", 180)


def test_unknown_joint_raises():
    arm = HumanoidArm()
    with pytest.raises(JointLimitError):
        arm.validate_joint_limits("ankle", 10)


def test_validate_all_passes_for_valid_configuration():
    arm = HumanoidArm()
    arm.validate_all([0, 0, 0])  # should not raise


def test_validate_all_raises_on_first_invalid_joint():
    arm = HumanoidArm()
    with pytest.raises(JointLimitError):
        arm.validate_all([0, 200, 0])  # elbow out of range