"""
test_lexer.py

Phase 2 unit tests — Lexer.
"""

import pytest
from humanoidscript.lexer.lexer import Lexer, LexError
from humanoidscript.lexer.tokens import TokenType


def _token_types(tokens):
    return [t.type for t in tokens if t.type != TokenType.EOF]


def test_walk_command_lexer():
    tokens = Lexer("walk forward 2m").tokenize()

    assert tokens[0].type == TokenType.KEYWORD
    assert tokens[0].value == "walk"

    assert tokens[1].type == TokenType.KEYWORD
    assert tokens[1].value == "forward"

    assert tokens[2].type == TokenType.NUMBER
    assert tokens[2].value == 2

    assert tokens[3].type == TokenType.UNIT
    assert tokens[3].value == "m"


def test_turn_command_lexer():
    tokens = Lexer("turn right 90deg").tokenize()

    assert tokens[0].value == "turn"
    assert tokens[1].value == "right"
    assert tokens[2].value == 90
    assert tokens[3].value == "deg"


def test_variable_declaration_lexer():
    tokens = Lexer("let speed = 0.5").tokenize()

    assert tokens[0].value == "let"
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "speed"
    assert tokens[2].type == TokenType.OPERATOR
    assert tokens[2].value == "="
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[3].value == 0.5


def test_string_literal_lexer():
    tokens = Lexer('let name = "H1"').tokenize()

    string_token = tokens[3]
    assert string_token.type == TokenType.STRING
    assert string_token.value == "H1"


def test_multi_char_operators():
    tokens = Lexer("x == y").tokenize()
    assert tokens[1].type == TokenType.OPERATOR
    assert tokens[1].value == "=="


def test_comments_are_ignored():
    tokens = Lexer("let x = 1 # this is a comment").tokenize()
    values = [t.value for t in tokens]
    assert "#" not in values
    assert "this" not in values


def test_newline_tokens_are_emitted():
    tokens = Lexer("let x = 1\nlet y = 2").tokenize()
    assert TokenType.NEWLINE in _token_types(tokens)


def test_unknown_character_raises_lex_error():
    with pytest.raises(LexError):
        Lexer("let x = @").tokenize()


def test_eof_token_is_always_last():
    tokens = Lexer("let x = 1").tokenize()
    assert tokens[-1].type == TokenType.EOF