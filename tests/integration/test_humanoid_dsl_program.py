"""
test_humanoid_dsl_program.py

Phase 4 integration tests — full HumanoidScript programs combining
control flow (Phase 3) with humanoid commands (Phase 4), run end
to end through the Interpreter.
"""

import pytest
from humanoidscript.runtime.interpreter import execute
from humanoidscript.robotics.errors import HumanoidStateError


def test_pick_and_place_program_executes_in_order():
    runtime = execute("""
        robot H1

        stand

        walk forward 2m
        turn right 90deg

        reach right_hand to bottle
        grasp bottle

        walk forward 1m

        release bottle
    """)

    assert runtime.humanoid.robot_name == "H1"
    assert runtime.humanoid.log == [
        "[HUMANOID] Robot 'H1' declared",
        "[HUMANOID] Standing",
        "[HUMANOID] Walking forward 2m",
        "[HUMANOID] Turning right 90deg",
        "[HUMANOID] Reaching with right_hand to bottle",
        "[HUMANOID] Grasping bottle",
        "[HUMANOID] Walking forward 1m",
        "[HUMANOID] Releasing bottle",
    ]


def test_walk_before_stand_raises_error():
    with pytest.raises(HumanoidStateError):
        execute("""
            robot H1
            walk forward 2m
        """)


def test_conditional_humanoid_behavior():
    """
    Combines Phase 3 control flow with Phase 4 humanoid commands:
    only reach for the bottle if a simulated 'object_detected' flag
    is true.
    """
    runtime = execute("""
        robot H1
        stand

        let object_detected = true

        if object_detected:
            reach right_hand to bottle
            grasp bottle
        else:
            turn right 90deg
        end
    """)

    assert runtime.humanoid.is_holding("bottle") is True
    assert "[HUMANOID] Turning right 90deg" not in runtime.humanoid.log


def test_loop_of_walk_commands():
    runtime = execute("""
        robot H1
        stand

        let steps = 0

        while steps < 3:
            walk forward 1m
            let steps = steps + 1
        end
    """)

    walk_logs = [line for line in runtime.humanoid.log if "Walking" in line]
    assert len(walk_logs) == 3