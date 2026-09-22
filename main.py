#!/usr/bin/env python3
"""
main.py

Phase 7 — HumanoidScript CLI.

Usage:
    humanoid run <file.hum>      Execute a HumanoidScript program.
    humanoid check <file.hum>    Validate syntax without running it.
"""

import sys
import argparse

from humanoidscript.lexer.lexer import Lexer, LexError
from humanoidscript.parser.parser import Parser, ParseError
from humanoidscript.runtime.interpreter import Interpreter
from humanoidscript.runtime.errors import HumanoidRuntimeError
from humanoidscript.robotics.errors import (
    HumanoidStateError,
    InvalidHandError,
    JointLimitError,
    UnreachableTargetError,
    IKConvergenceError,
    CollisionError,
    BalanceViolationError,
)

ROBOTICS_ERRORS = (
    HumanoidStateError,
    InvalidHandError,
    JointLimitError,
    UnreachableTargetError,
    IKConvergenceError,
    CollisionError,
    BalanceViolationError,
)


def _read_source(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def run_file(path: str) -> int:
    try:
        source = _read_source(path)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        return 1

    try:
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
    except LexError as e:
        print(f"LEX ERROR:\n{e}")
        return 1
    except ParseError as e:
        print(f"PARSE ERROR:\n{e}")
        return 1

    interpreter = Interpreter()
    try:
        interpreter.interpret(program)
    except ROBOTICS_ERRORS as e:
        print(f"ROBOTICS ERROR:\n{e}")
        return 1
    except HumanoidRuntimeError as e:
        print(f"RUNTIME ERROR:\n{e}")
        return 1

    return 0


def check_file(path: str) -> int:
    try:
        source = _read_source(path)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        return 1

    try:
        tokens = Lexer(source).tokenize()
        Parser(tokens).parse()
    except LexError as e:
        print(f"LEX ERROR:\n{e}")
        return 1
    except ParseError as e:
        print(f"PARSE ERROR:\n{e}")
        return 1

    print(f"{path}: syntax OK")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="humanoid")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a HumanoidScript program")
    run_parser.add_argument("file", help="Path to .hum file")

    check_parser = subparsers.add_parser("check", help="Check syntax without running")
    check_parser.add_argument("file", help="Path to .hum file")

    args = parser.parse_args(argv)

    if args.command == "run":
        return run_file(args.file)
    if args.command == "check":
        return check_file(args.file)

    return 1


if __name__ == "__main__":
    sys.exit(main())