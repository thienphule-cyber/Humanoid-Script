"""
lexer.py

Phase 2 — Lexer.

Converts HumanoidScript source code into a flat list of Tokens.

Example:
    "walk forward 2m"
        -> KEYWORD(walk), KEYWORD(forward), NUMBER(2), UNIT(m)
"""

from humanoidscript.lexer.tokens import Token, TokenType
from humanoidscript.lexer.language_spec import (
    KEYWORDS,
    UNITS,
    is_keyword,
    is_unit,
)

# Multi-character operators must be checked before single-character ones
MULTI_CHAR_OPERATORS = ["==", "!=", "<=", ">="]
SINGLE_CHAR_OPERATORS = ["+", "-", "*", "/", "=", "<", ">"]


class LexError(Exception):
    """Raised when the lexer encounters an invalid character/token."""
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        while not self._at_end():
            self._scan_token()

        self.tokens.append(Token(TokenType.EOF, None, self.line))
        return self.tokens

    # -----------------------------------------------------------
    # Core scanning
    # -----------------------------------------------------------
    def _scan_token(self) -> None:
        char = self._peek()

        if char in " \t":
            self.pos += 1
            return

        if char == "\n":
            self.tokens.append(Token(TokenType.NEWLINE, None, self.line))
            self.line += 1
            self.pos += 1
            return

        if char == "#":
            self._skip_comment()
            return

        if char.isdigit():
            self._scan_number()
            return

        if char.isalpha() or char == "_":
            self._scan_identifier_or_keyword()
            return

        if char == '"':
            self._scan_string()
            return

        if char == "(":
            self.tokens.append(Token(TokenType.LPAREN, "(", self.line))
            self.pos += 1
            return

        if char == ")":
            self.tokens.append(Token(TokenType.RPAREN, ")", self.line))
            self.pos += 1
            return

        if char == ",":
            self.tokens.append(Token(TokenType.COMMA, ",", self.line))
            self.pos += 1
            return

        if char == ":":
            self.tokens.append(Token(TokenType.COLON, ":", self.line))
            self.pos += 1
            return

        if self._scan_operator():
            return

        raise LexError(f"Line {self.line}: Unexpected character {char!r}")

    # -----------------------------------------------------------
    # Sub-scanners
    # -----------------------------------------------------------
    def _scan_number(self) -> None:
        start = self.pos
        while not self._at_end() and self._peek().isdigit():
            self.pos += 1

        if not self._at_end() and self._peek() == "." and self._peek_next().isdigit():
            self.pos += 1
            while not self._at_end() and self._peek().isdigit():
                self.pos += 1

        text = self.source[start:self.pos]
        value = float(text) if "." in text else int(text)
        self.tokens.append(Token(TokenType.NUMBER, value, self.line))

        # Immediately following unit, e.g. "2m" or "90deg" (no space)
        self._maybe_scan_attached_unit()

    def _maybe_scan_attached_unit(self) -> None:
        start = self.pos
        while not self._at_end() and self._peek().isalpha():
            self.pos += 1

        word = self.source[start:self.pos]
        if word == "":
            return

        if is_unit(word):
            self.tokens.append(Token(TokenType.UNIT, word, self.line))
        else:
            # Not a unit: rewind, let identifier/keyword scanning handle it
            self.pos = start

    def _scan_identifier_or_keyword(self) -> None:
        start = self.pos
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self.pos += 1

        word = self.source[start:self.pos]

        if is_keyword(word):
            self.tokens.append(Token(TokenType.KEYWORD, word, self.line))
        elif is_unit(word):
            self.tokens.append(Token(TokenType.UNIT, word, self.line))
        else:
            self.tokens.append(Token(TokenType.IDENTIFIER, word, self.line))

    def _scan_string(self) -> None:
        self.pos += 1  # consume opening quote
        start = self.pos

        while not self._at_end() and self._peek() != '"':
            if self._peek() == "\n":
                self.line += 1
            self.pos += 1

        if self._at_end():
            raise LexError(f"Line {self.line}: Unterminated string literal")

        text = self.source[start:self.pos]
        self.pos += 1  # consume closing quote
        self.tokens.append(Token(TokenType.STRING, text, self.line))

    def _scan_operator(self) -> bool:
        remaining = self.source[self.pos:self.pos + 2]
        if remaining in MULTI_CHAR_OPERATORS:
            self.tokens.append(Token(TokenType.OPERATOR, remaining, self.line))
            self.pos += 2
            return True

        char = self._peek()
        if char in SINGLE_CHAR_OPERATORS:
            self.tokens.append(Token(TokenType.OPERATOR, char, self.line))
            self.pos += 1
            return True

        return False

    def _skip_comment(self) -> None:
        while not self._at_end() and self._peek() != "\n":
            self.pos += 1

    # -----------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------
    def _at_end(self) -> bool:
        return self.pos >= len(self.source)

    def _peek(self) -> str:
        return self.source[self.pos]

    def _peek_next(self) -> str:
        if self.pos + 1 >= len(self.source):
            return "\0"
        return self.source[self.pos + 1]