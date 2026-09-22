"""
scene.py

Phase 6 — Scene management.

Holds named objects placed in the simulated environment (e.g. a
bottle, a table) so that humanoid commands like `reach right_hand
to bottle` can be resolved to an actual (x, y) target position.

This is intentionally minimal: objects are static points, with no
physics or 3D geometry. It is a lookup table with a friendly API.
"""

from dataclasses import dataclass


@dataclass
class SceneObject:
    name: str
    x: float
    y: float


class ObjectNotFoundError(Exception):
    """Raised when a scene object is looked up by a name that doesn't exist."""
    pass


class Scene:
    def __init__(self):
        self._objects: dict[str, SceneObject] = {}

    def add_object(self, name: str, x: float, y: float) -> None:
        self._objects[name] = SceneObject(name=name, x=x, y=y)

    def get_object(self, name: str) -> SceneObject:
        if name not in self._objects:
            raise ObjectNotFoundError(f"No object named {name!r} in scene")
        return self._objects[name]

    def remove_object(self, name: str) -> None:
        if name not in self._objects:
            raise ObjectNotFoundError(f"No object named {name!r} in scene")
        del self._objects[name]

    def has_object(self, name: str) -> bool:
        return name in self._objects

    def list_objects(self) -> list:
        return list(self._objects.values())