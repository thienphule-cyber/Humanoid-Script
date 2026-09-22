"""
test_language_spec.py

Phase 1 unit tests.

These tests validate the language specification tables
(keywords, units, data types, operators) before any lexer
or parser logic is built on top of them.
"""

from humanoidscript.lexer.language_spec import (
    KEYWORDS,
    UNITS,
    DATA_TYPES,
    ARITHMETIC_OPERATORS,
    COMPARISON_OPERATORS,
    ASSIGNMENT_OPERATORS,
    ALL_OPERATORS,
    FILE_EXTENSION,
    is_keyword,
    is_unit,
    is_operator,
)


# -----------------------------------------------------------
# Keyword table tests
# -----------------------------------------------------------
def test_core_control_flow_keywords_exist():
    assert "if" in KEYWORDS
    assert "else" in KEYWORDS
    assert "while" in KEYWORDS
    assert "function" in KEYWORDS
    assert "return" in KEYWORDS


def test_humanoid_command_keywords_exist():
    assert "walk" in KEYWORDS
    assert "turn" in KEYWORDS
    assert "reach" in KEYWORDS
    assert "grasp" in KEYWORDS
    assert "release" in KEYWORDS


def test_direction_keywords_exist():
    assert "forward" in KEYWORDS
    assert "backward" in KEYWORDS
    assert "left" in KEYWORDS
    assert "right" in KEYWORDS


def test_is_keyword_helper():
    assert is_keyword("walk") is True
    assert is_keyword("banana") is False


# -----------------------------------------------------------
# Unit table tests
# -----------------------------------------------------------
def test_distance_units_exist():
    assert "m" in UNITS
    assert "cm" in UNITS


def test_angle_units_exist():
    assert "deg" in UNITS
    assert "rad" in UNITS


def test_is_unit_helper():
    assert is_unit("deg") is True
    assert is_unit("kg") is False  # not a supported unit


# -----------------------------------------------------------
# Data type table tests
# -----------------------------------------------------------
def test_data_types_defined():
    assert "number" in DATA_TYPES
    assert "string" in DATA_TYPES
    assert "boolean" in DATA_TYPES
    assert "array" in DATA_TYPES


# -----------------------------------------------------------
# Operator table tests
# -----------------------------------------------------------
def test_arithmetic_operators():
    assert "+" in ARITHMETIC_OPERATORS
    assert "-" in ARITHMETIC_OPERATORS
    assert "*" in ARITHMETIC_OPERATORS
    assert "/" in ARITHMETIC_OPERATORS


def test_comparison_operators():
    assert "==" in COMPARISON_OPERATORS
    assert "!=" in COMPARISON_OPERATORS
    assert "<=" in COMPARISON_OPERATORS
    assert ">=" in COMPARISON_OPERATORS


def test_assignment_operator():
    assert "=" in ASSIGNMENT_OPERATORS


def test_all_operators_is_union_of_categories():
    expected = (
        ARITHMETIC_OPERATORS
        | COMPARISON_OPERATORS
        | ASSIGNMENT_OPERATORS
    )
    assert ALL_OPERATORS == expected


def test_is_operator_helper():
    assert is_operator("+") is True
    assert is_operator("^") is False  # not supported yet


# -----------------------------------------------------------
# File extension test
# -----------------------------------------------------------
def test_file_extension_is_hum():
    assert FILE_EXTENSION == ".hum"


# -----------------------------------------------------------
# Consistency test: no overlap between keywords and units
# -----------------------------------------------------------
def test_keywords_and_units_do_not_overlap():
    """
    A word should not be both a keyword and a unit,
    otherwise the lexer (Phase 2) would have ambiguity
    when tokenizing.
    """
    assert KEYWORDS.isdisjoint(UNITS)