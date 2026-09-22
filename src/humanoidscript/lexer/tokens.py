"""
tokens.py

Phase 2 — Token definitions for the HumanoidScript lexer.

Defines the TokenType enum and the Token dataclass used
throughout the lexer and parser.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Units (m, cm, deg, rad, s)
    UNIT = auto()

    # Keywords (let, walk, if, function, ...)
    KEYWORD = auto()

    # Operators (+, -, *, /, ==, !=, <, >, <=, >=, =)
    OPERATOR = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    COLON = auto()

    # Statement separator
    NEWLINE = auto()

    # End of file marker
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, line={self.line})"