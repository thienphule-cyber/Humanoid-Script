"""
test_balance.py

Phase 6 unit tests — Balance / center of mass checking.
"""

import pytest
from humanoidscript.robotics.balance import (
    SupportPolygon,
    compute_center_of_mass,
    check_balance,
)
from humanoidscript.robotics.errors import BalanceViolationError


def test_support_polygon_contains_point_inside_range():
    support = SupportPolygon(min_x=-0.5, max_x=0.5)
    assert support.contains(0.0) is True
    assert support.contains(0.4) is True


def test_support_polygon_rejects_point_outside_range():
    support = SupportPolygon(min_x=-0.5, max_x=0.5)
    assert support.contains(0.6) is False
    assert support.contains(-0.6) is False


def test_compute_center_of_mass_unweighted_average():
    positions = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]
    com_x, com_y = compute_center_of_mass(positions)

    assert com_x == pytest.approx(1.0)
    assert com_y == pytest.approx(0.0)


def test_compute_center_of_mass_weighted_by_mass():
    positions = [(0.0, 0.0), (2.0, 0.0)]
    masses = [3.0, 1.0]  # heavier near x=0, so COM should shift toward 0

    com_x, _ = compute_center_of_mass(positions, masses=masses)

    assert com_x == pytest.approx(0.5)  # (0*3 + 2*1) / 4


def test_compute_center_of_mass_empty_positions_raises():
    with pytest.raises(ValueError):
        compute_center_of_mass([])


def test_compute_center_of_mass_mismatched_masses_raises():
    with pytest.raises(ValueError):
        compute_center_of_mass([(0, 0), (1, 0)], masses=[1.0])


def test_check_balance_stable_does_not_raise():
    positions = [(0.0, 0.0), (0.1, 0.0)]
    support = SupportPolygon(min_x=-0.5, max_x=0.5)

    check_balance(positions, support)  # should not raise


def test_check_balance_unstable_raises():
    positions = [(2.0, 0.0), (2.5, 0.0)]
    support = SupportPolygon(min_x=-0.5, max_x=0.5)

    with pytest.raises(BalanceViolationError):
        check_balance(positions, support)