"""
environment.py

Phase 3 — Environment (variable scope).

A chain of scopes for variable storage: the global scope, plus a
new child scope created for each function call, so that variables
declared inside a function do not leak into the caller's scope.
"""

from typing import Any, Optional


class Environment:
    def __init__(self, parent: Optional["Environment"] = None):
        self.parent = parent
        self.values: dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        """Define (or redefine) a variable in the current scope."""
        self.values[name] = value

    def get(self, name: str) -> Any:
        """Look up a variable, walking up parent scopes if needed."""
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise KeyError(name)

    def assign(self, name: str, value: Any) -> None:
        """Assign to an existing variable, walking up parent scopes."""
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value)
            return
        raise KeyError(name)

    def is_defined(self, name: str) -> bool:
        if name in self.values:
            return True
        if self.parent is not None:
            return self.parent.is_defined(name)
        return False