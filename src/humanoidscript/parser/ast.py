"""
ast.py

Phase 2/3/7 — Abstract Syntax Tree node definitions.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


class ASTNode:
    """Base marker class for all AST nodes."""
    pass


@dataclass
class Program(ASTNode):
    statements: list[ASTNode] = field(default_factory=list)


# -----------------------------------------------------------
# Expressions
# -----------------------------------------------------------
@dataclass
class NumberLiteral(ASTNode):
    value: float
    unit: Optional[str] = None


@dataclass
class StringLiteral(ASTNode):
    value: str


@dataclass
class BooleanLiteral(ASTNode):
    value: bool


@dataclass
class Identifier(ASTNode):
    name: str


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: list[ASTNode] = field(default_factory=list)


# -----------------------------------------------------------
# Statements
# -----------------------------------------------------------
@dataclass
class VariableDeclaration(ASTNode):
    name: str
    value: ASTNode


@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode


@dataclass
class RobotDeclaration(ASTNode):
    name: str


@dataclass
class ObjectDeclaration(ASTNode):
    """Phase 7: `object <name> at (x, y)` — places a static object
    in the scene so `reach` commands can resolve it to a real
    position for the robotics engine."""
    name: str
    x: float
    y: float


# -----------------------------------------------------------
# Control flow (Phase 3)
# -----------------------------------------------------------
@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_body: list[ASTNode] = field(default_factory=list)
    else_body: Optional[list[ASTNode]] = None


@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: list[ASTNode] = field(default_factory=list)


@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    parameters: list[str] = field(default_factory=list)
    body: list[ASTNode] = field(default_factory=list)


@dataclass
class ReturnStatement(ASTNode):
    expression: Optional[ASTNode] = None


# -----------------------------------------------------------
# Humanoid commands
# -----------------------------------------------------------
@dataclass
class WalkCommand(ASTNode):
    direction: str
    distance: float
    unit: str


@dataclass
class TurnCommand(ASTNode):
    direction: str
    angle: float
    unit: str


@dataclass
class StandCommand(ASTNode):
    pass


@dataclass
class ReachCommand(ASTNode):
    hand: str
    target: str


@dataclass
class GraspCommand(ASTNode):
    target: str


@dataclass
class ReleaseCommand(ASTNode):
    target: str