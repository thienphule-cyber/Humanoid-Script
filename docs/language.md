# HumanoidScript Language Reference

HumanoidScript is a small, line-oriented language. Each statement
occupies its own line; blocks (`if`, `while`, `function`) are closed
with an explicit `end` keyword rather than indentation.

File extension: `.hum`

## Comments
This is a comment, ignored by the lexer

let x = 1 # inline comments are also supported


## Data types

| Type    | Example         |
|---------|-----------------|
| number  | `42`, `0.5`     |
| string  | `"H1"`          |
| boolean | `true`, `false` |

Numbers may carry a unit suffix, used by humanoid commands:

| Unit   | Meaning  |
|--------|----------|
| `m`    | meters   |
| `cm`   | centimeters |
| `deg`  | degrees  |
| `rad`  | radians  |
| `s`    | seconds  |

## Variables

let speed = 0.5
let name = "H1"
let ready = true


Variables are dynamically typed and reassignable with another `let`.

## Operators

| Category    | Operators                     |
|-------------|--------------------------------|
| Arithmetic  | `+`  `-`  `*`  `/`             |
| Comparison  | `==` `!=` `<` `>` `<=` `>=`    |
| Assignment  | `=`                             |

Standard precedence applies: `*`/`/` bind tighter than `+`/`-`,
which bind tighter than comparisons. Parentheses `(...)` override
precedence.

## Control flow

### if / else

if x > 5:
print("high")
else:
print("low")
end


The `else` branch is optional.

### while

let counter = 0

while counter < 5:
print(counter)
let counter = counter + 1
end


### Functions

function add(a, b):
return a + b
end

let result = add(2, 3)
print(result)


A function called purely for its side effects can also be used as
a bare statement:

function greet(name):
print(name)
end

greet("Kelvin")


### print

print("hello")
print(x + y)


## Humanoid commands

### robot

Declares the robot being programmed. Currently symbolic (naming
only); does not affect execution.

robot H1


### object ... at (x, y)

Places a named object in the scene at position `(x, y)`, in meters,
relative to the arm's shoulder (the origin). This makes the object
a valid target for `reach` — without this declaration, `reach`
commands referencing the name still work, but only as a symbolic
log entry (no real kinematics is computed).

object bottle at (0.4, 0.1)
object cup at (0.3, -0.1)


### stand

Marks the robot as standing. Required before `walk`, `turn`, or
`reach`.

stand


### walk

walk <direction> <distance><unit>


`<direction>` is one of `forward`, `backward`, `left`, `right`.

walk forward 2m


### turn

turn <direction> <angle><unit>

turn right 90deg


### reach

reach <hand> to <target>


`<hand>` is `right_hand` or `left_hand`. If `<target>` was declared
with `object ... at (x, y)`, inverse kinematics, trajectory
generation, joint-limit checking, and collision checking all run
for real; the simulator's arm actually moves. If `<target>` was
never declared, the command still succeeds as a symbolic log entry.

reach right_hand to bottle


### grasp

grasp <target>


Requires that the same hand has already `reach`ed the target, and
that the hand is not already holding something else.

grasp bottle


### release

release <target>


Requires that `<target>` is currently held by some hand.

release bottle


## Full example

robot H1

object bottle at (0.3, 0.1)

stand

walk forward 2m
turn right 90deg

reach right_hand to bottle
grasp bottle

walk forward 1m

release bottle