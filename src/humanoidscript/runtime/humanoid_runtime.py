"""
humanoid_runtime.py

Phase 4/7 — Humanoid Control DSL runtime, integrated with the
robotics engine and simulator.

Translates high-level humanoid commands (stand, walk, turn, reach,
grasp, release) into:
  1. A human-readable log
  2. A list of structured ExecutedCommand objects
  3. (Phase 7) Real kinematics execution when the target of a
     `reach` command has been placed in the scene via an
     `object <name> at (x, y)` statement.

Scope note: this project models a single representative arm
kinematic chain (robotics.humanoid.HumanoidArm). Both "right_hand"
and "left_hand" share this same simulated chain; the hand name is
used only for bookkeeping (which hand is holding what), not as two
independently simulated arms.

Backward compatibility: if `reach` targets an object that was never
declared in the scene, the command still succeeds as a purely
symbolic log entry (matching the original Phase 4 behavior), since
there is no physical position to compute kinematics against.
"""

from typing import Optional

from humanoidscript.robotics.commands import (
    ExecutedCommand,
    RobotDeclared,
    StandExecuted,
    WalkExecuted,
    TurnExecuted,
    ReachExecuted,
    GraspExecuted,
    ReleaseExecuted,
)
from humanoidscript.robotics.errors import HumanoidStateError, InvalidHandError
from humanoidscript.robotics.humanoid import HumanoidArm
from humanoidscript.robotics.ik import inverse_kinematics
from humanoidscript.robotics.trajectory import generate_trajectory
from humanoidscript.simulation.scene import Scene
from humanoidscript.simulation.simulator import Simulator

VALID_HANDS = {"right_hand", "left_hand"}


class HumanoidRuntime:
    def __init__(
        self,
        arm: Optional[HumanoidArm] = None,
        scene: Optional[Scene] = None,
        simulator: Optional[Simulator] = None,
    ):
        self.robot_name: Optional[str] = None
        self.is_standing: bool = False

        self.held: dict[str, Optional[str]] = {
            "right_hand": None,
            "left_hand": None,
        }
        self._last_reached: dict[str, Optional[str]] = {
            "right_hand": None,
            "left_hand": None,
        }

        self.log: list[str] = []
        self.commands: list[ExecutedCommand] = []

        self.arm = arm if arm is not None else HumanoidArm()
        self.scene = scene if scene is not None else Scene()
        self.simulator = simulator if simulator is not None else Simulator(arm=self.arm)

    # -----------------------------------------------------------
    # Commands
    # -----------------------------------------------------------
    def declare_robot(self, name: str) -> None:
        self.robot_name = name
        self._record(f"[HUMANOID] Robot '{name}' declared", RobotDeclared(name=name))

    def stand(self) -> None:
        self.is_standing = True
        self._record("[HUMANOID] Standing", StandExecuted())

    def walk(self, direction: str, distance: float, unit: str) -> None:
        self._require_standing("walk")
        self._record(
            f"[HUMANOID] Walking {direction} {distance}{unit}",
            WalkExecuted(direction=direction, distance=distance, unit=unit),
        )

    def turn(self, direction: str, angle: float, unit: str) -> None:
        self._require_standing("turn")
        self._record(
            f"[HUMANOID] Turning {direction} {angle}{unit}",
            TurnExecuted(direction=direction, angle=angle, unit=unit),
        )

    def reach(self, hand: str, target: str) -> None:
        self._require_valid_hand(hand)
        self._require_standing("reach")

        if self.scene.has_object(target):
            scene_object = self.scene.get_object(target)
            q_target = inverse_kinematics(
                self.arm,
                scene_object.x,
                scene_object.y,
                initial_guess=self.simulator.current_q,
            )
            trajectory = generate_trajectory(self.simulator.current_q, q_target)
            # Propagates UnreachableTargetError, IKConvergenceError,
            # CollisionError, JointLimitError, or BalanceViolationError
            # from the robotics engine, if applicable.
            self.simulator.execute(trajectory)

        self._last_reached[hand] = target
        self._record(
            f"[HUMANOID] Reaching with {hand} to {target}",
            ReachExecuted(hand=hand, target=target),
        )

    def grasp(self, target: str) -> None:
        hand = self._find_hand_that_reached(target)
        if hand is None:
            raise HumanoidStateError(
                f"Cannot grasp {target!r}: no hand has reached it yet"
            )
        if self.held[hand] is not None:
            raise HumanoidStateError(
                f"Cannot grasp {target!r}: {hand} is already holding "
                f"{self.held[hand]!r}"
            )

        self.held[hand] = target
        self._record(
            f"[HUMANOID] Grasping {target}",
            GraspExecuted(target=target),
        )

    def release(self, target: str) -> None:
        hand = self._find_hand_holding(target)
        if hand is None:
            raise HumanoidStateError(
                f"Cannot release {target!r}: it is not currently held"
            )

        self.held[hand] = None
        self._record(
            f"[HUMANOID] Releasing {target}",
            ReleaseExecuted(target=target),
        )

    # -----------------------------------------------------------
    # Queries
    # -----------------------------------------------------------
    def is_holding(self, target: str) -> bool:
        return target in self.held.values()

    def holding_in(self, hand: str) -> Optional[str]:
        self._require_valid_hand(hand)
        return self.held[hand]

    # -----------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------
    def _require_standing(self, action: str) -> None:
        if not self.is_standing:
            raise HumanoidStateError(
                f"Cannot {action}: robot must be standing first"
            )

    def _require_valid_hand(self, hand: str) -> None:
        if hand not in VALID_HANDS:
            raise InvalidHandError(
                f"{hand!r} is not a valid hand (expected one of {sorted(VALID_HANDS)})"
            )

    def _find_hand_that_reached(self, target: str) -> Optional[str]:
        for hand, reached_target in self._last_reached.items():
            if reached_target == target:
                return hand
        return None

    def _find_hand_holding(self, target: str) -> Optional[str]:
        for hand, held_target in self.held.items():
            if held_target == target:
                return hand
        return None

    def _record(self, log_line: str, command: ExecutedCommand) -> None:
        self.log.append(log_line)
        self.commands.append(command)