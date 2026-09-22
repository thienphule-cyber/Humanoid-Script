# HumanoidScript

A software-only domain-specific programming language for expressing
humanoid robot behaviors at multiple levels of abstraction — from raw
joint control up to task-level commands like `walk`, `reach`, and
`grasp` — with a custom lexer, parser, interpreter, robotics engine,
and simulator. No hardware required; the entire pipeline runs on a
laptop.

robot H1

object bottle at (0.4, 0.1)

stand

walk forward 2m
turn right 90deg

reach right_hand to bottle
grasp bottle

walk forward 1m

release bottle


## Why

Controlling a humanoid robot normally means working with low-level
APIs (`set_joint_angle`, `compute_ik`, `send_trajectory`, ...) and
juggling many joints, limbs, and constraints at once.
HumanoidScript adds an abstraction layer on top: a small language
whose runtime translates high-level commands into real kinematics,
trajectory generation, and collision/joint-limit checking.

## Features

- A hand-written lexer, parser, and tree-walking interpreter
- Variables, arithmetic/comparison expressions, `if/else`, `while`,
  user-defined functions
- Humanoid DSL commands: `robot`, `object ... at (x, y)`, `stand`,
  `walk`, `turn`, `reach`, `grasp`, `release`
- A robotics engine: forward kinematics, inverse kinematics (damped
  Jacobian with null-space secondary objective and joint-limit
  clamping), joint limits, linear trajectory interpolation, and
  circular-obstacle collision checking
- A simulator that tracks robot state (joint configuration,
  end-effector pose, movement history) independently of any
  rendering/visualization layer
- A simplified balance check (center of mass vs. support polygon)
- A CLI (`humanoid run` / `humanoid check`)
- 133 automated tests (pytest), covering every layer of the pipeline

See [`docs/architecture.md`](docs/architecture.md) for the full
pipeline, [`docs/language.md`](docs/language.md) for the language
reference, and [`docs/robotics.md`](docs/robotics.md) for the
kinematics/robotics engine details.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Usage

Run a program:

```bash
humanoid run examples/pick_and_place.hum
```

Check syntax without running:

```bash
humanoid check examples/pick_and_place.hum
```

(If you skipped `pip install -e .`, use `python main.py run <file>`
instead, or set `PYTHONPATH=src` first.)

## Project layout

src/humanoidscript/
├── lexer/ # Lexer, tokens, language specification
├── parser/ # Parser, AST node definitions
├── runtime/ # Interpreter, environment, humanoid runtime
├── robotics/ # Humanoid arm model, FK, IK, trajectory, collision, balance
└── simulation/ # Simulator (state) and Scene (object placement)

tests/ # pytest suite, mirroring the structure above
examples/ # Example .hum programs
docs/ # Architecture, language, and robotics reference docs


## Running tests

```bash
pytest -v
```

## Scope and design notes

This project models a single representative 3-DOF planar arm chain
(shoulder → elbow → wrist) rather than a full multi-limb humanoid
body. This keeps the kinematics, IK, and collision logic tractable
for a personal project while still demonstrating the full concept
end to end. Extending to legs, a torso, or a second independently
simulated arm would mean adding more `HumanoidArm` instances and
reusing the same `kinematics`/`ik`/`trajectory` modules.