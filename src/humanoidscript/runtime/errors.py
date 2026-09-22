"""
errors.py

Phase 3 — Runtime error types and internal control-flow signals.
"""


class HumanoidRuntimeError(Exception):
    """Base class for all runtime errors raised during interpretation."""
    pass


class UndefinedVariableError(HumanoidRuntimeError):
    def __init__(self, name: str):
        super().__init__(f"Undefined variable: {name!r}")
        self.name = name


class UndefinedFunctionError(HumanoidRuntimeError):
    def __init__(self, name: str):
        super().__init__(f"Undefined function: {name!r}")
        self.name = name


class ArityMismatchError(HumanoidRuntimeError):
    def __init__(self, function_name: str, expected: int, got: int):
        super().__init__(
            f"Function {function_name!r} expects {expected} argument(s), got {got}"
        )


class ReturnSignal(Exception):
    """
    Internal control-flow signal used to unwind execution when a
    'return' statement runs. Not a user-facing error — caught
    internally by the interpreter's function-call handler.
    """
    def __init__(self, value):
        self.value = value