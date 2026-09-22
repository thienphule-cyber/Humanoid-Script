# Architecture

## Pipeline overview

Source (.hum file)
│
▼
Lexer source text -> flat list of Tokens
│
▼
Parser Tokens -> AST (Program node)
│
▼
Interpreter walks the AST, executes statements/expressions
│
▼
HumanoidRuntime humanoid DSL command state machine
│
▼
Robotics Engine FK / IK / trajectory / collision / joint limits
│
▼
Simulator tracks robot state (joints, pose, history)


Each stage is a separate module with its own test suite, so a bug
in one layer (say, the parser) can be isolated without touching the
layers above or below it.

## Module map

src/humanoidscript/
│
├── lexer/
│ ├── language_spec.py keyword/unit/operator tables (Phase 1)
│ ├── tokens.py TokenType enum, Token dataclass
│ └── lexer.py Lexer: source -> Tokens
│
├── parser/
│ ├── ast.py AST node dataclasses
│ └── parser.py recursive-descent Parser: Tokens -> AST
│
├── runtime/
│ ├── environment.py variable scope chain
│ ├── errors.py interpreter-level error types
│ ├── interpreter.py tree-walking interpreter
│ └── humanoid_runtime.py humanoid DSL command dispatch + state
│
├── robotics/
│ ├── humanoid.py HumanoidArm model, joint limits
│ ├── kinematics.py forward kinematics
│ ├── ik.py inverse kinematics solver
│ ├── trajectory.py joint-space trajectory generation
│ ├── collision.py obstacle collision checking
│ ├── balance.py center-of-mass / support polygon
│ ├── commands.py executed-command records
│ └── errors.py robotics-domain error types
│
└── simulation/
├── simulator.py state tracking (joints, pose, history)
└── scene.py named object placement


## Data flow for a `reach` command

This is the most involved path in the system, since it touches
every layer from Phase 4 through Phase 7:

Interpreter sees a ReachCommand AST node
│
▼
HumanoidRuntime.reach(hand, target)
│
├── target NOT in Scene?
│ → record a symbolic log entry only (Phase 4 behavior)
│
└── target IS in Scene (has a real x, y)?
│
▼
robotics.ik.inverse_kinematics(arm, x, y, ...)
│ (damped Jacobian + null-space bias + joint-limit
│ clamping + active-set freezing + random multi-start)
▼
robotics.trajectory.generate_trajectory(current_q, target_q)
│ (linear interpolation, so the arm doesn't teleport)
▼
Simulator.execute(trajectory)
│ (re-validates joint limits at every waypoint,
│ checks collisions against any declared obstacles,
│ updates simulator.current_q and history)
▼
HumanoidRuntime records the ReachExecuted command + log line


If IK cannot converge, the target is unreachable, a joint limit
would be violated, or a collision is detected, the corresponding
robotics-domain error propagates all the way up through the
interpreter to the CLI, which reports it as a `ROBOTICS ERROR` and
exits with a non-zero status.

## Design principle: logic vs. rendering

The `Simulator` class only manages state — joint configuration,
end-effector pose, and a history of every waypoint executed. It
contains no drawing code. This split means:

- Everything in `Simulator` is unit-testable with pytest.
- A visualization layer (2D/3D rendering, built separately and out
  of scope for the current test suite) would read from
  `simulator.history` / `simulator.current_pose()` rather than being
  entangled with the physics/kinematics logic itself.

## Backward compatibility across phases

Each phase was built to extend, not break, the previous one:

- Phase 4's humanoid commands work purely symbolically (log-only).
- Phase 7 adds real kinematics for `reach`, but **only** when the
  target has been placed in the scene via `object ... at (x, y)`.
  A `reach` to an undeclared target still falls back to the
  Phase 4 symbolic behavior, so older/simpler `.hum` programs keep
  working unmodified.

## CLI

`main.py` provides two subcommands:

- `humanoid check <file.hum>` — runs the lexer and parser only, to
  validate syntax without executing anything.
- `humanoid run <file.hum>` — runs the full pipeline. Errors at any
  stage (lex, parse, robotics, or general runtime) are caught,
  labeled by category, and reported with a non-zero exit code.