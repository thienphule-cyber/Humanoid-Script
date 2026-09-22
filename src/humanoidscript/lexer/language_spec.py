"""
language_spec.py

Phase 1/7 — Language Design & Specification.

This module defines the core vocabulary of HumanoidScript:
keywords, supported units, data types, and operators.
"""

KEYWORDS = {
    "let",
    "if",
    "else",
    "while",
    "for",
    "function",
    "return",
    "end",
    "print",

    "robot",
    "object",  # Phase 7: `object <name> at (x, y)` scene placement

    "stand",
    "sit",
    "posture",
    "walk",
    "turn",
    "look",
    "reach",
    "grasp",
    "release",

    "forward",
    "backward",
    "left",
    "right",

    "true",
    "false",
}

UNITS = {
    "m",
    "cm",
    "deg",
    "rad",
    "s",
}

DATA_TYPES = {
    "number",
    "string",
    "boolean",
    "array",
}

ARITHMETIC_OPERATORS = {"+", "-", "*", "/"}
COMPARISON_OPERATORS = {"==", "!=", "<", ">", "<=", ">="}
ASSIGNMENT_OPERATORS = {"="}

ALL_OPERATORS = (
    ARITHMETIC_OPERATORS
    | COMPARISON_OPERATORS
    | ASSIGNMENT_OPERATORS
)

FILE_EXTENSION = ".hum"


def is_keyword(word: str) -> bool:
    return word in KEYWORDS


def is_unit(word: str) -> bool:
    return word in UNITS


def is_operator(symbol: str) -> bool:
    return symbol in ALL_OPERATORS