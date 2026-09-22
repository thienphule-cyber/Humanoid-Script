"""
test_scene.py

Phase 6 unit tests — Scene object management.
"""

import pytest
from humanoidscript.simulation.scene import Scene, ObjectNotFoundError


def test_add_and_get_object():
    scene = Scene()
    scene.add_object("bottle", x=0.5, y=0.2)

    obj = scene.get_object("bottle")
    assert obj.name == "bottle"
    assert obj.x == 0.5
    assert obj.y == 0.2


def test_get_missing_object_raises():
    scene = Scene()
    with pytest.raises(ObjectNotFoundError):
        scene.get_object("bottle")


def test_has_object():
    scene = Scene()
    assert scene.has_object("table") is False

    scene.add_object("table", x=1.0, y=0.0)
    assert scene.has_object("table") is True


def test_remove_object():
    scene = Scene()
    scene.add_object("bottle", x=0.5, y=0.2)
    scene.remove_object("bottle")

    assert scene.has_object("bottle") is False


def test_remove_missing_object_raises():
    scene = Scene()
    with pytest.raises(ObjectNotFoundError):
        scene.remove_object("bottle")


def test_list_objects_returns_all_added_objects():
    scene = Scene()
    scene.add_object("bottle", x=0.5, y=0.2)
    scene.add_object("table", x=1.0, y=0.0)

    names = {obj.name for obj in scene.list_objects()}
    assert names == {"bottle", "table"}


def test_add_object_overwrites_existing_with_same_name():
    scene = Scene()
    scene.add_object("bottle", x=0.5, y=0.2)
    scene.add_object("bottle", x=0.6, y=0.3)  # moved

    obj = scene.get_object("bottle")
    assert obj.x == 0.6
    assert obj.y == 0.3