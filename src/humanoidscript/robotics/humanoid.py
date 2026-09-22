"""
humanoid.py

Phase 5 — Humanoid arm model.

Defines a simplified planar 3-DOF arm (shoulder, elbow, wrist)
used as the representative kinematic chain for this project.
Real humanoid robots have many more joints (legs, torso, head),
but a single arm chain is enough to demonstrate FK, IK, joint
limits, trajectory generation, and collision checking end to end.

All angles are stored/validated in degrees at the model boundary
(since that matches HumanoidScript source syntax, e.g. "45deg"),
but kinematics computations internally use radians.
"""

from dataclasses import dataclass, field

from humanoidscript.robotics.errors import JointLimitError

JOINT_NAMES = ["shoulder", "elbow", "wrist"]

# (min_degrees, max_degrees) per joint
DEFAULT_JOINT_LIMITS = {
    "shoulder": (-90.0, 150.0),
    "elbow": (-10.0, 120.0),
    "wrist": (-90.0, 90.0),
}

# Link lengths in meters
DEFAULT_LINK_LENGTHS = {
    "shoulder_to_elbow": 0.30,
    "elbow_to_wrist": 0.25,
    "wrist_to_end_effector": 0.10,
}


@dataclass
class HumanoidArm:
    """
    A simplified 3-DOF planar arm model.

    joint_limits: dict of joint_name -> (min_deg, max_deg)
    link_lengths: dict of link_name -> length_in_meters
    """
    joint_limits: dict = field(default_factory=lambda: dict(DEFAULT_JOINT_LIMITS))
    link_lengths: dict = field(default_factory=lambda: dict(DEFAULT_LINK_LENGTHS))

    @property
    def total_reach(self) -> float:
        """Maximum distance the end-effector can be from the shoulder."""
        return sum(self.link_lengths.values())

    def validate_joint_limits(self, joint_name: str, angle_deg: float) -> None:
        if joint_name not in self.joint_limits:
            raise JointLimitError(f"Unknown joint: {joint_name!r}")

        min_deg, max_deg = self.joint_limits[joint_name]
        if not (min_deg <= angle_deg <= max_deg):
            raise JointLimitError(
                f"Joint {joint_name!r} angle {angle_deg}deg out of range. "
                f"Allowed range: {min_deg}deg to {max_deg}deg"
            )

    def validate_all(self, q_deg: list) -> None:
        """Validate a full joint configuration, given in degrees,
        ordered [shoulder, elbow, wrist]."""
        for joint_name, angle_deg in zip(JOINT_NAMES, q_deg):
            self.validate_joint_limits(joint_name, angle_deg)