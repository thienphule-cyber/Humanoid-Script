"""
simulator.py

Phase 6 — Humanoid Simulator.

Executes joint-space trajectories against a HumanoidArm model and
keeps track of the robot's current state (joint configuration,
end-effector pose, movement history). This class contains no
rendering code — it is the state layer that a visual front-end
(outside the scope of automated tests) would read from.

Design principle from the project plan:
    Robotics Logic (unit tested)
           |
           v
    Simulation Renderer (not unit tested — visual only)

This module is the "Robotics Logic" / state side.
"""

from dataclasses import dataclass, field
from typing import Optional

from humanoidscript.robotics.humanoid import HumanoidArm, JOINT_NAMES
from humanoidscript.robotics.kinematics import forward_kinematics, joint_positions, EndEffectorPose
from humanoidscript.robotics.collision import Obstacle, check_trajectory_collision
from humanoidscript.robotics.balance import SupportPolygon, check_balance
from humanoidscript.robotics.errors import JointLimitError


@dataclass
class SimulatorState:
    """A snapshot of the simulator at one point in time."""
    joints: list  # [shoulder_rad, elbow_rad, wrist_rad]
    end_effector: EndEffectorPose


class Simulator:
    def __init__(
        self,
        arm: Optional[HumanoidArm] = None,
        initial_q: Optional[list] = None,
        obstacles: Optional[list] = None,
        support_polygon: Optional[SupportPolygon] = None,
    ):
        self.arm = arm if arm is not None else HumanoidArm()
        self.current_q = list(initial_q) if initial_q is not None else [0.0, 0.0, 0.0]
        self.obstacles: list[Obstacle] = obstacles if obstacles is not None else []
        self.support_polygon = support_polygon  # None means balance checking is skipped

        self.history: list[SimulatorState] = []
        self._record_state()

    # -----------------------------------------------------------
    # Execution
    # -----------------------------------------------------------
    def execute(self, trajectory: list, check_collision: bool = True, check_balance_at_each_step: bool = False) -> None:
        """
        Steps the simulator through every waypoint of `trajectory`
        (a list of [shoulder, elbow, wrist] joint configs, in radians,
        as produced by robotics.trajectory.generate_trajectory).

        If check_collision is True (default), the whole trajectory is
        validated against self.obstacles before any state is updated,
        so a colliding trajectory leaves the simulator state unchanged.

        If check_balance_at_each_step is True and a support_polygon was
        provided, each waypoint's center of mass is checked for balance.
        """
        if check_collision and self.obstacles:
            check_trajectory_collision(self.arm, trajectory, self.obstacles)

        for q in trajectory:
            self.arm.validate_all([_rad_to_deg(v) for v in q])

            if check_balance_at_each_step and self.support_polygon is not None:
                positions = joint_positions(self.arm, q)
                check_balance(positions, self.support_polygon)

            self.current_q = list(q)
            self._record_state()

    def reset(self, q: Optional[list] = None) -> None:
        """Resets the simulator to a given configuration (default: all zeros)."""
        self.current_q = list(q) if q is not None else [0.0, 0.0, 0.0]
        self.history = []
        self._record_state()

    # -----------------------------------------------------------
    # Queries
    # -----------------------------------------------------------
    def current_pose(self) -> EndEffectorPose:
        return forward_kinematics(self.arm, self.current_q)

    def current_joint_positions(self) -> list:
        return joint_positions(self.arm, self.current_q)

    def steps_executed(self) -> int:
        """Number of waypoints applied so far (excluding the initial state)."""
        return len(self.history) - 1

    # -----------------------------------------------------------
    # Internal
    # -----------------------------------------------------------
    def _record_state(self) -> None:
        pose = forward_kinematics(self.arm, self.current_q)
        self.history.append(SimulatorState(joints=list(self.current_q), end_effector=pose))


def _rad_to_deg(value: float) -> float:
    import math
    return math.degrees(value)