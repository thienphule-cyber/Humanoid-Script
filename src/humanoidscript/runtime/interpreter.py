"""
interpreter.py

Phase 3 — Interpreter & Runtime.

Tree-walking interpreter that executes a HumanoidScript AST
(Program node) produced by the Parser.

Supports: variables, arithmetic, comparisons, booleans,
if/else, while loops, functions, return, and lexical scope.

Humanoid-specific commands (walk, turn, reach, ...) are accepted
by the parser but not yet executed here — that begins in Phase 4.
"""

from humanoidscript.lexer.lexer import Lexer
from humanoidscript.parser.parser import Parser
from humanoidscript.parser.ast import (
    Program,
    NumberLiteral,
    StringLiteral,
    BooleanLiteral,
    Identifier,
    BinaryOp,
    FunctionCall,
    VariableDeclaration,
    PrintStatement,
    RobotDeclaration,
    ObjectDeclaration,
    IfStatement,
    WhileStatement,
    FunctionDeclaration,
    ReturnStatement,
    WalkCommand,
    TurnCommand,
    StandCommand,
    ReachCommand,
    GraspCommand,
    ReleaseCommand,
)
from humanoidscript.runtime.humanoid_runtime import HumanoidRuntime
from humanoidscript.runtime.environment import Environment
from humanoidscript.runtime.errors import (
    HumanoidRuntimeError,
    UndefinedVariableError,
    UndefinedFunctionError,
    ArityMismatchError,
    ReturnSignal,
)


class _FunctionObject:
    """Internal representation of a user-defined function."""

    def __init__(self, name: str, parameters: list[str], body: list):
        self.name = name
        self.parameters = parameters
        self.body = body


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.functions: dict[str, _FunctionObject] = {}
        self.output: list[str] = []
        self.humanoid = HumanoidRuntime()

    # -----------------------------------------------------------
    # Public API
    # -----------------------------------------------------------
    def interpret(self, program: Program) -> None:
        for stmt in program.statements:
            self._execute(stmt, self.global_env)

    def get(self, name: str):
        """Look up a global variable by name (used by tests)."""
        try:
            return self.global_env.get(name)
        except KeyError:
            raise UndefinedVariableError(name)

    # -----------------------------------------------------------
    # Statement execution
    # -----------------------------------------------------------
    def _execute(self, node, env: Environment):
        if isinstance(node, VariableDeclaration):
            value = self._evaluate(node.value, env)
            env.define(node.name, value)
            return

        if isinstance(node, PrintStatement):
            value = self._evaluate(node.expression, env)
            text = self._to_display(value)
            self.output.append(text)
            print(text)
            return

        if isinstance(node, IfStatement):
            condition = self._evaluate(node.condition, env)
            if self._is_truthy(condition):
                for stmt in node.then_body:
                    self._execute(stmt, env)
            elif node.else_body is not None:
                for stmt in node.else_body:
                    self._execute(stmt, env)
            return

        if isinstance(node, WhileStatement):
            while self._is_truthy(self._evaluate(node.condition, env)):
                for stmt in node.body:
                    self._execute(stmt, env)
            return

        if isinstance(node, FunctionDeclaration):
            self.functions[node.name] = _FunctionObject(
                name=node.name,
                parameters=node.parameters,
                body=node.body,
            )
            return

        if isinstance(node, ReturnStatement):
            value = (
                self._evaluate(node.expression, env)
                if node.expression is not None
                else None
            )
            raise ReturnSignal(value)

        if isinstance(node, RobotDeclaration):
            self.humanoid.declare_robot(node.name)
            return
        
        if isinstance(node, ObjectDeclaration):
            self.humanoid.scene.add_object(node.name, node.x, node.y)
            return

        if isinstance(node, StandCommand):
            self.humanoid.stand()
            return

        if isinstance(node, WalkCommand):
            self.humanoid.walk(node.direction, node.distance, node.unit)
            return

        if isinstance(node, TurnCommand):
            self.humanoid.turn(node.direction, node.angle, node.unit)
            return

        if isinstance(node, ReachCommand):
            self.humanoid.reach(node.hand, node.target)
            return

        if isinstance(node, GraspCommand):
            self.humanoid.grasp(node.target)
            return

        if isinstance(node, ReleaseCommand):
            self.humanoid.release(node.target)
            return

        # FunctionCall used as a bare statement (e.g. calling a function
        # purely for its side effects, ignoring the return value).
        if isinstance(node, FunctionCall):
            self._evaluate(node, env)
            return

        raise HumanoidRuntimeError(
            f"Interpreter does not yet support statement: {type(node).__name__}"
        )

    # -----------------------------------------------------------
    # Expression evaluation
    # -----------------------------------------------------------
    def _evaluate(self, node, env: Environment):
        if isinstance(node, NumberLiteral):
            return node.value

        if isinstance(node, StringLiteral):
            return node.value

        if isinstance(node, BooleanLiteral):
            return node.value

        if isinstance(node, Identifier):
            try:
                return env.get(node.name)
            except KeyError:
                raise UndefinedVariableError(node.name)

        if isinstance(node, BinaryOp):
            return self._evaluate_binary_op(node, env)

        if isinstance(node, FunctionCall):
            return self._call_function(node, env)

        raise HumanoidRuntimeError(
            f"Interpreter does not yet support expression: {type(node).__name__}"
        )

    def _evaluate_binary_op(self, node: BinaryOp, env: Environment):
        left = self._evaluate(node.left, env)
        right = self._evaluate(node.right, env)
        op = node.operator

        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            if right == 0:
                raise HumanoidRuntimeError("Division by zero")
            return left / right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            return left < right
        if op == ">":
            return left > right
        if op == "<=":
            return left <= right
        if op == ">=":
            return left >= right

        raise HumanoidRuntimeError(f"Unsupported operator: {op!r}")

    def _call_function(self, node: FunctionCall, env: Environment):
        func = self.functions.get(node.name)
        if func is None:
            raise UndefinedFunctionError(node.name)

        if len(node.arguments) != len(func.parameters):
            raise ArityMismatchError(
                func.name, len(func.parameters), len(node.arguments)
            )

        call_env = Environment(parent=self.global_env)
        for param_name, arg_node in zip(func.parameters, node.arguments):
            call_env.define(param_name, self._evaluate(arg_node, env))

        try:
            for stmt in func.body:
                self._execute(stmt, call_env)
        except ReturnSignal as signal:
            return signal.value

        return None  # function had no explicit return

    # -----------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------
    @staticmethod
    def _is_truthy(value) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return bool(value)

    @staticmethod
    def _to_display(value) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if value is None:
            return "none"
        return str(value)


def execute(source: str) -> Interpreter:
    """
    Convenience function: lex + parse + interpret a HumanoidScript
    source string in one call.

    Returns the Interpreter instance so callers can inspect global
    variables (interpreter.get(name)) and captured print output
    (interpreter.output).
    """
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()

    interpreter = Interpreter()
    interpreter.interpret(program)
    return interpreter