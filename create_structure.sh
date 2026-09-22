#!/usr/bin/env bash
# create_structure.sh
# Creates the full HumanoidScript project skeleton (empty files + folders)

set -e

echo "Creating HumanoidScript project structure..."

# Root source package
mkdir -p src/humanoidscript/lexer
mkdir -p src/humanoidscript/parser
mkdir -p src/humanoidscript/runtime
mkdir -p src/humanoidscript/robotics
mkdir -p src/humanoidscript/simulation

# Tests (mirrors src structure)
mkdir -p tests/lexer
mkdir -p tests/parser
mkdir -p tests/runtime
mkdir -p tests/robotics
mkdir -p tests/simulation
mkdir -p tests/integration

# Examples, docs, ci
mkdir -p examples
mkdir -p docs
mkdir -p .github/workflows

# --- src/humanoidscript ---
touch src/humanoidscript/__init__.py

# lexer
touch src/humanoidscript/lexer/__init__.py
touch src/humanoidscript/lexer/lexer.py
touch src/humanoidscript/lexer/tokens.py

# parser
touch src/humanoidscript/parser/__init__.py
touch src/humanoidscript/parser/parser.py
touch src/humanoidscript/parser/ast.py

# runtime
touch src/humanoidscript/runtime/__init__.py
touch src/humanoidscript/runtime/interpreter.py
touch src/humanoidscript/runtime/environment.py
touch src/humanoidscript/runtime/errors.py

# robotics
touch src/humanoidscript/robotics/__init__.py
touch src/humanoidscript/robotics/humanoid.py
touch src/humanoidscript/robotics/kinematics.py
touch src/humanoidscript/robotics/ik.py
touch src/humanoidscript/robotics/trajectory.py
touch src/humanoidscript/robotics/collision.py
touch src/humanoidscript/robotics/balance.py

# simulation
touch src/humanoidscript/simulation/__init__.py
touch src/humanoidscript/simulation/scene.py
touch src/humanoidscript/simulation/simulator.py

# --- tests ---
touch tests/__init__.py

touch tests/lexer/__init__.py
touch tests/lexer/test_lexer.py

touch tests/parser/__init__.py
touch tests/parser/test_parser.py

touch tests/runtime/__init__.py
touch tests/runtime/test_interpreter.py

touch tests/robotics/__init__.py
touch tests/robotics/test_kinematics.py
touch tests/robotics/test_ik.py
touch tests/robotics/test_trajectory.py
touch tests/robotics/test_collision.py
touch tests/robotics/test_balance.py

touch tests/simulation/__init__.py
touch tests/simulation/test_simulator.py

touch tests/integration/__init__.py
touch tests/integration/test_pick_and_place.py

# --- examples ---
touch examples/hello.hum
touch examples/walking.hum
touch examples/reaching.hum
touch examples/grasping.hum
touch examples/pick_and_place.hum

# --- docs ---
touch docs/language.md
touch docs/architecture.md
touch docs/robotics.md

# --- CI ---
touch .github/workflows/tests.yml

# --- root files ---
touch main.py
touch pyproject.toml
touch README.md
touch .gitignore

echo "Done. Project structure created."