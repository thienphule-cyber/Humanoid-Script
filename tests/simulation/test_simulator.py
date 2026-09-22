"""
test_simulator.py

Phase 6 unit tests — Simulator state management.
"""

import math
import pytest
from humanoidscript.simulation.simulator import Simulator
from humanoidscript.robotics.humanoid import HumanoidArm
from humanoidscript.robotics.trajectory import generate_trajectory
from humanoidscript.robotics.collision import Obstacle
from humanoidscript.robotics.balance import SupportPolygon
from humanoidscript.robotics.errors import CollisionError, JointLimitError, BalanceViolationError


def test_simulator_initial_state_is_zero_configuration():
    sim = Simulator()
    assert sim.current_q == [0.0, 0.0, 0.0]
    assert len(sim.history) == 1


def test_simulator_updates_joint_state_after_execute():
    sim = Simulator()
    trajectory = generate_trajectory([0, 0, 0], [0.5, 0.3, 0.1], steps=5)

    sim.execute(trajectory)

    assert sim.current_q == pytest.approx(trajectory[-1])


def test_simulator_records_full_history():
    sim = Simulator()
    trajectory = generate_trajectory([0, 0, 0], [0.2, 0, 0], steps=10)

    sim.execute(trajectory)

    # initial state + 10 waypoints
    assert len(sim.history) == 11
    assert sim.steps_executed() == 10


def test_simulator_current_pose_matches_forward_kinematics():
    sim = Simulator()
    trajectory = generate_trajectory([0, 0, 0], [math.radians(30), 0, 0], steps=5)

    sim.execute(trajectory)
    pose = sim.current_pose()

    assert pose.x == pytest.approx(sim.arm.link_lengths["shoulder_to_elbow"]
                                    * math.cos(math.radians(30))
                                    + sim.arm.link_lengths["elbow_to_wrist"] * math.cos(math.radians(30))
                                    + sim.arm.link_lengths["wrist_to_end_effector"] * math.cos(math.radians(30)),
                                    abs=1e-3)


def test_simulator_reset_clears_history():
    sim = Simulator()
    trajectory = generate_trajectory([0, 0, 0], [0.5, 0, 0], steps=5)
    sim.execute(trajectory)

    sim.reset()

    assert sim.current_q == [0.0, 0.0, 0.0]
    assert len(sim.history) == 1


def test_simulator_reset_to_custom_configuration():
    sim = Simulator()
    sim.reset(q=[0.1, 0.2, 0.3])

    assert sim.current_q == [0.1, 0.2, 0.3]


def test_simulator_detects_collision_and_does_not_update_state():
    arm = HumanoidArm()
    obstacle = Obstacle(x=0.65, y=0.0, radius=0.05)  # sits at the zero-config end-effector
    sim = Simulator(arm=arm, obstacles=[obstacle])

    trajectory = generate_trajectory([0, 0, 0], [0, 0, 0], steps=2)

    with pytest.raises(CollisionError):
        sim.execute(trajectory)

    # State must remain unchanged since collision was detected before commit
    assert sim.current_q == [0.0, 0.0, 0.0]
    assert len(sim.history) == 1


def test_simulator_raises_on_joint_limit_violation():
    sim = Simulator()
    # elbow max is 120 deg; 200 deg exceeds it
    trajectory = [[0.0, math.radians(200), 0.0]]

    with pytest.raises(JointLimitError):
        sim.execute(trajectory)


def test_simulator_balance_check_passes_when_stable():
    support = SupportPolygon(min_x=-1.0, max_x=1.0)
    sim = Simulator(support_polygon=support)

    trajectory = generate_trajectory([0, 0, 0], [0.2, 0, 0], steps=3)

    # Should not raise — end effector stays well within [-1, 1]
    sim.execute(trajectory, check_balance_at_each_step=True)


def test_simulator_balance_check_raises_when_unstable():
    support = SupportPolygon(min_x=-0.01, max_x=0.01)  # very tight base
    sim = Simulator(support_polygon=support)

    trajectory = generate_trajectory([0, 0, 0], [0.2, 0, 0], steps=3)

    with pytest.raises(BalanceViolationError):
        sim.execute(trajectory, check_balance_at_each_step=True)