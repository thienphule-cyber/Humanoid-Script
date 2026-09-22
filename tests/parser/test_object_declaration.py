"""
test_object_declaration.py

Phase 7 unit tests — `object <name> at (x, y)` statement parsing.
"""

from humanoidscript.lexer.lexer import Lexer
from humanoidscript.parser.parser import Parser
from humanoidscript.parser.ast import ObjectDeclaration


def test_object_declaration_parses_correctly():
    tokens = Lexer("object bottle at (0.3, 0.15)").tokenize()
    program = Parser(tokens).parse()

    stmt = program.statements[0]
    assert isinstance(stmt, ObjectDeclaration)
    assert stmt.name == "bottle"
    assert stmt.x == 0.3
    assert stmt.y == 0.15