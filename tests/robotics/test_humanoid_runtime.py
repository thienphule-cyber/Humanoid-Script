"""
test_humanoid_runtime.py

Phase 4 unit tests — HumanoidRuntime (command execution + state).
"""

import pytest
from humanoidscript.runtime.humanoid_runtime import HumanoidRuntime
from humanoidscript.robotics.errors import HumanoidStateError, InvalidHandError
from humanoidscript.robotics.commands import (
    RobotDeclared,
    StandExecuted,
    WalkExecuted,
    TurnExecuted,
    ReachExecuted,
    GraspExecuted,
    ReleaseExecuted,
)


def test_declare_robot_sets_name_and_logs():
    runtime = HumanoidRuntime()
    runtime.declare_robot("H1")

    assert runtime.robot_name == "H1"
    assert isinstance(runtime.commands[0], RobotDeclared)
    assert runtime.commands[0].name == "H1"
    assert "[HUMANOID] Robot 'H1' declared" in runtime.log


def test_stand_sets_standing_state():
    runtime = HumanoidRuntime()
    runtime.stand()

    assert runtime.is_standing is True
    assert isinstance(runtime.commands[0], StandExecuted)


def test_walk_requires_standing_first():
    runtime = HumanoidRuntime()

    with pytest.raises(HumanoidStateError):
        runtime.walk("forward", 2, "m")


def test_walk_after_standing_succeeds():
    runtime = HumanoidRuntime()
    runtime.stand()
    runtime.walk("forward", 2, "m")

    walk_cmd = runtime.commands[-1]
    assert isinstance(walk_cmd, WalkExecuted)
    assert walk_cmd.direction == "forward"
    assert walk_cmd.distance == 2
    assert walk_cmd.unit == "m"
    assert "[HUMANOID] Walking forward 2m" in runtime.log


def test_turn_requires_standing_first():
    runtime = HumanoidRuntime()

    with pytest.raises(HumanoidStateError):
        runtime.turn("right", 90, "deg")


def test_turn_after_standing_succeeds():
    runtime = HumanoidRuntime()
    runtime.stand()
    runtime.turn("right", 90, "deg")

    turn_cmd = runtime.commands[-1]
    assert isinstance(turn_cmd, TurnExecuted)
    assert turn_cmd.direction == "right"
    assert turn_cmd.angle == 90


def test_reach_with_invalid_hand_raises_error():
    runtime = HumanoidRuntime()
    runtime.stand()

    with pytest.raises(InvalidHandError):
        runtime.reach("middle_hand", "bottle")


def test_reach_records_target_per_hand():
    runtime = HumanoidRuntime()
    runtime.stand()
    runtime.reach("right_hand", "bottle")

    reach_cmd = runtime.commands[-1]
    assert isinstance(reach_cmd, ReachExecuted)
    assert reach_cmd.hand == "right_hand"
    assert reach_cmd.target == "bottle"


def test_grasp_without_reach_raises_error():
    runtime = HumanoidRuntime()
    runtime.stand()

    with pytest.raises(HumanoidStateError):
        runtime.grasp("bottle")


def test_grasp_after_reach_succeeds():
    runtime = HumanoidRuntime()
    runtime.stand()
    runtime.reach("right_hand", "bottle")
    runtime.grasp("bottle")

    assert runtime.holding_in("right_hand") == "bottle"
    assert runtime.is_holding("bottle") is True
    assert isinstance(runtime.commands[-1], GraspExecuted)


def test_grasp_same_hand_twice_raises_error():
    runtime = HumanoidRuntime()
    runtime.stand()
    runtime.reach("right_hand", "bottle")
    runtime.grasp("bottle")

    runtime.reach("right_hand", "cup")
    with pytest.raises(HumanoidStateError):
        runtime.grasp("cup")  # right_hand is already full


def test_release_without_holding_raises_error():
    runtime = HumanoidRuntime()
    runtime.stand()

    with pytest.raises(HumanoidStateError):
        runtime.release("bottle")


def test_release_after_grasp_succeeds():
    runtime = HumanoidRuntime()
    runtime.stand()
    runtime.reach("right_hand", "bottle")
    runtime.grasp("bottle")
    runtime.release("bottle")

    assert runtime.holding_in("right_hand") is None
    assert runtime.is_holding("bottle") is False
    assert isinstance(runtime.commands[-1], ReleaseExecuted)


def test_full_pick_sequence_produces_expected_log_order():
    runtime = HumanoidRuntime()
    runtime.declare_robot("H1")
    runtime.stand()
    runtime.walk("forward", 2, "m")
    runtime.turn("right", 90, "deg")
    runtime.reach("right_hand", "bottle")
    runtime.grasp("bottle")
    runtime.release("bottle")

    assert runtime.log == [
        "[HUMANOID] Robot 'H1' declared",
        "[HUMANOID] Standing",
        "[HUMANOID] Walking forward 2m",
        "[HUMANOID] Turning right 90deg",
        "[HUMANOID] Reaching with right_hand to bottle",
        "[HUMANOID] Grasping bottle",
        "[HUMANOID] Releasing bottle",
    ]