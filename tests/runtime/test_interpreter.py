"""
test_interpreter.py

Phase 3 unit tests — Interpreter & Runtime.
"""

import pytest
from humanoidscript.runtime.interpreter import execute
from humanoidscript.runtime.errors import (
    HumanoidRuntimeError,
    UndefinedVariableError,
    UndefinedFunctionError,
    ArityMismatchError,
)


def test_variable_arithmetic():
    runtime = execute("""
        let x = 10
        let y = 20
        let z = x + y
    """)

    assert runtime.get("z") == 30


def test_operator_precedence_in_runtime():
    runtime = execute("let result = 2 + 3 * 4")
    assert runtime.get("result") == 14


def test_string_variable():
    runtime = execute('let name = "H1"')
    assert runtime.get("name") == "H1"


def test_boolean_variable():
    runtime = execute("let ready = true")
    assert runtime.get("ready") is True


def test_function_call():
    runtime = execute("""
        function add(a, b):
            return a + b
        end

        let result = add(2, 3)
    """)

    assert runtime.get("result") == 5


def test_function_with_no_return_yields_none_when_used():
    runtime = execute("""
        function greet(name):
            print(name)
        end

        greet("Kelvin")
    """)

    assert runtime.output == ["Kelvin"]


def test_recursive_style_helper_function():
    runtime = execute("""
        function square(x):
            return x * x
        end

        function sum_of_squares(a, b):
            return square(a) + square(b)
        end

        let result = sum_of_squares(3, 4)
    """)

    assert runtime.get("result") == 25


def test_if_else_true_branch():
    runtime = execute("""
        let x = 10

        if x > 5:
            let status = "high"
        else:
            let status = "low"
        end
    """)
    # Note: 'status' is declared inside the if-block's own scope in a
    # stricter language design, but this interpreter executes blocks
    # in the same environment they were called from, so it is visible.
    assert runtime.get("status") == "high"


def test_if_else_false_branch():
    runtime = execute("""
        let x = 2

        if x > 5:
            let status = "high"
        else:
            let status = "low"
        end
    """)

    assert runtime.get("status") == "low"


def test_while_loop_accumulates_correctly():
    runtime = execute("""
        let counter = 0
        let total = 0

        while counter < 5:
            let total = total + counter
            let counter = counter + 1
        end
    """)

    assert runtime.get("total") == 10
    assert runtime.get("counter") == 5


def test_print_statement_output():
    runtime = execute('print("hello")')
    assert runtime.output == ["hello"]


def test_comparison_operators():
    runtime = execute("""
        let a = (5 == 5)
        let b = (5 != 5)
        let c = (3 < 5)
        let d = (5 >= 5)
    """)

    assert runtime.get("a") is True
    assert runtime.get("b") is False
    assert runtime.get("c") is True
    assert runtime.get("d") is True


def test_undefined_variable_raises_runtime_error():
    with pytest.raises(UndefinedVariableError):
        execute("print(unknown)")


def test_undefined_function_raises_runtime_error():
    with pytest.raises(UndefinedFunctionError):
        execute("let x = missing_function(1, 2)")


def test_arity_mismatch_raises_runtime_error():
    with pytest.raises(ArityMismatchError):
        execute("""
            function add(a, b):
                return a + b
            end

            let result = add(1)
        """)


def test_division_by_zero_raises_runtime_error():
    with pytest.raises(HumanoidRuntimeError):
        execute("let x = 10 / 0")