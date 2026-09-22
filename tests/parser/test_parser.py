"""
test_parser.py

Phase 2 unit tests — Parser & AST.
"""

import pytest
from humanoidscript.lexer.lexer import Lexer
from humanoidscript.parser.parser import Parser, ParseError
from humanoidscript.parser.ast import (
    VariableDeclaration,
    WalkCommand,
    TurnCommand,
    BinaryOp,
    NumberLiteral,
    Identifier,
    ReachCommand,
    GraspCommand,
    StandCommand,
)


def _parse(source: str):
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()


def test_variable_declaration_parser():
    program = _parse("let speed = 0.5")

    stmt = program.statements[0]
    assert isinstance(stmt, VariableDeclaration)
    assert stmt.name == "speed"
    assert isinstance(stmt.value, NumberLiteral)
    assert stmt.value.value == 0.5


def test_walk_command_parser():
    program = _parse("walk forward 2m")

    stmt = program.statements[0]
    assert isinstance(stmt, WalkCommand)
    assert stmt.direction == "forward"
    assert stmt.distance == 2
    assert stmt.unit == "m"


def test_turn_command_parser():
    program = _parse("turn right 90deg")

    stmt = program.statements[0]
    assert isinstance(stmt, TurnCommand)
    assert stmt.direction == "right"
    assert stmt.angle == 90
    assert stmt.unit == "deg"


def test_stand_command_parser():
    program = _parse("stand")
    assert isinstance(program.statements[0], StandCommand)


def test_reach_command_parser():
    program = _parse("reach right_hand to bottle")

    stmt = program.statements[0]
    assert isinstance(stmt, ReachCommand)
    assert stmt.hand == "right_hand"
    assert stmt.target == "bottle"


def test_grasp_command_parser():
    program = _parse("grasp bottle")

    stmt = program.statements[0]
    assert isinstance(stmt, GraspCommand)
    assert stmt.target == "bottle"


def test_binary_expression_precedence():
    """2 + 3 * 4 should parse as 2 + (3 * 4), not (2 + 3) * 4."""
    program = _parse("let result = 2 + 3 * 4")

    decl = program.statements[0]
    assert isinstance(decl, VariableDeclaration)

    top = decl.value
    assert isinstance(top, BinaryOp)
    assert top.operator == "+"
    assert isinstance(top.left, NumberLiteral)
    assert top.left.value == 2

    right = top.right
    assert isinstance(right, BinaryOp)
    assert right.operator == "*"
    assert right.left.value == 3
    assert right.right.value == 4


def test_identifier_expression():
    program = _parse("let z = x")

    decl = program.statements[0]
    assert isinstance(decl.value, Identifier)
    assert decl.value.name == "x"


def test_multiple_statements_separated_by_newline():
    program = _parse("let x = 1\nlet y = 2")
    assert len(program.statements) == 2


def test_invalid_walk_direction_raises_parse_error():
    with pytest.raises(ParseError):
        _parse("walk banana 2m")


def test_missing_unit_raises_parse_error():
    with pytest.raises(ParseError):
        _parse("walk forward 2")


def test_unexpected_token_raises_parse_error():
    with pytest.raises(ParseError):
        _parse("2 + 3")  # bare expression is not a valid statement yet