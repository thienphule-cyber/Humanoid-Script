"""
test_pick_and_place.py

Phase 7 integration tests — full HumanoidScript programs exercising
the complete pipeline: Lexer -> Parser -> AST -> Interpreter ->
HumanoidRuntime -> Robotics Engine (IK/trajectory/collision) ->
Simulator state.
"""

import pytest
from humanoidscript.runtime.interpreter import execute
from humanoidscript.robotics.errors import UnreachableTargetError, HumanoidStateError


def test_full_pick_and_place_program():
    runtime = execute("""
        robot H1

        object bottle at (0.3, 0.1)

        stand

        walk forward 2m
        turn right 90deg

        reach right_hand to bottle
        grasp bottle

        walk forward 1m

        release bottle
    """)

    assert runtime.humanoid.robot_name == "H1"
    assert runtime.humanoid.scene.has_object("bottle")

    # Real IK was solved, so the simulator's end-effector actually
    # moved to the declared object position (not just a log line).
    pose = runtime.humanoid.simulator.current_pose()
    assert pose.x == pytest.approx(0.3, abs=1e-3)
    assert pose.y == pytest.approx(0.1, abs=1e-3)

    assert "[HUMANOID] Grasping bottle" in runtime.humanoid.log
    assert "[HUMANOID] Releasing bottle" in runtime.humanoid.log


def test_reach_to_undeclared_object_falls_back_to_symbolic_logging():
    """Backward-compatible with Phase 4: reaching for an object that
    was never declared via `object ... at (...)` still succeeds as a
    symbolic command, so older/simpler programs keep working."""
    runtime = execute("""
        robot H1
        stand
        reach right_hand to bottle
        grasp bottle
    """)

    assert runtime.humanoid.is_holding("bottle") is True
    assert runtime.humanoid.simulator.current_q == [0.0, 0.0, 0.0]


def test_reach_to_unreachable_declared_object_raises():
    with pytest.raises(UnreachableTargetError):
        execute("""
            robot H1
            object far_target at (10.0, 10.0)
            stand
            reach right_hand to far_target
        """)


def test_walk_before_stand_still_raises():
    with pytest.raises(HumanoidStateError):
        execute("""
            robot H1
            walk forward 2m
        """)


def test_multiple_objects_in_scene():
    runtime = execute("""
        robot H1

        object bottle at (0.3, 0.1)
        object cup at (0.3, -0.1)

        stand

        reach right_hand to bottle
        grasp bottle
        release bottle

        reach right_hand to cup
        grasp cup
    """)

    assert runtime.humanoid.is_holding("cup") is True
    assert runtime.humanoid.is_holding("bottle") is False