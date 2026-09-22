# Robotics Engine Reference

## Arm model

The project models a single representative kinematic chain: a
planar 3-DOF arm with three revolute joints in series.

Shoulder ──(0.30m)── Elbow ──(0.25m)── Wrist ──(0.10m)── End-effector


| Joint    | Limits (degrees) |
|----------|-------------------|
| shoulder | -90 to 150        |
| elbow    | -10 to 120        |
| wrist    | -90 to 90         |

Both `right_hand` and `left_hand` in the DSL share this same
simulated chain; the hand name is bookkeeping (which hand is
holding what), not two independently simulated arms.

Total reach: sum of the three link lengths (0.65m). Any target
farther than this from the shoulder is immediately rejected as
unreachable, before the IK solver even runs.

## Forward kinematics (FK)

Given joint angles `[shoulder, elbow, wrist]` (radians, all
measured relative to the previous link), FK computes the
end-effector's `(x, y)` position and orientation via standard
serial-chain trigonometry:

theta1 = q0
theta2 = q0 + q1
theta3 = q0 + q1 + q2

x = L1cos(theta1) + L2cos(theta2) + L3cos(theta3)
y = L1sin(theta1) + L2sin(theta2) + L3sin(theta3)


`robotics.kinematics.joint_positions()` additionally returns the
position of every joint along the chain (not just the
end-effector), which the balance and collision checks use.

## Inverse kinematics (IK)

Because the arm has 3 joints but a target position is only 2
constraints (x, y), the arm is kinematically redundant: infinitely
many joint configurations can reach the same point. The solver
handles this with several layered techniques:

1. **Damped least-squares Jacobian** (primary task): iteratively
   nudges the joint configuration toward the target using the
   pseudo-inverse of the Jacobian, with a small damping term for
   numerical stability near singularities.
2. **Null-space secondary objective**: among the many valid
   solutions, biases the result toward the neutral pose
   (`q = 0`), computed with an *exact* (non-damped) pseudo-inverse
   projector so it doesn't interfere with the primary task's
   convergence.
3. **Hard joint-limit clamping**: after every iteration, each joint
   angle is clamped into its allowed range, so the returned
   solution is always physically valid.
4. **Active-set freezing**: if a joint is sitting exactly at its
   limit and the current step would push it further out of bounds,
   that joint's update is frozen for the iteration instead of being
   silently clamped away — this prevents the solver from wasting
   iterations repeatedly trying (and failing) to cross a boundary.
5. **Random multi-start**: some targets have a *unique* solution
   that sits exactly at a joint-limit boundary ("corner solutions").
   A single starting guess can get stuck oscillating near such a
   corner. The solver tries the caller's `initial_guess` first, then
   a configurable number of randomly sampled starting configurations
   (with a fixed random seed, for reproducibility) until one
   converges.

Raises:
- `UnreachableTargetError` — target farther than the arm's total reach.
- `IKConvergenceError` — no starting attempt converged within the
  iteration budget. In practice this usually means the target,
  while geometrically within reach, requires a joint configuration
  that violates the joint limits from every tried starting pose.

### A note on target selection

Not every point within the arm's total reach is actually achievable
under the joint limits above. Some points require a joint angle to
sit exactly at (or beyond) its boundary, which makes them hard or
impossible to solve to tight tolerance. When placing new objects in
a `.hum` program, prefer coordinates with comfortable margin from
every joint's limits (e.g. `(0.3, 0.1)`, `(0.4, 0.1)`, `(0.5, 0.0)`)
over points requiring an extreme, boundary-hugging pose.

## Trajectory generation

Rather than teleporting the arm directly from its current
configuration to the IK solution, `robotics.trajectory` generates a
sequence of intermediate joint configurations via linear
interpolation:

q(t) = q_start + t * (q_end - q_start), t in [0, 1]


The `Simulator` steps through every waypoint in order, re-validating
joint limits and checking for collisions at each one — so a
trajectory that would clip an obstacle partway through is caught
even if both endpoints are individually collision-free.

Velocity/acceleration-constrained trajectories are a natural future
extension; the current implementation is intentionally simple.

## Collision checking

Obstacles are modeled as circles (`Obstacle(x, y, radius)`). A
trajectory collides if the end-effector's position at *any*
waypoint falls within an obstacle's radius (plus an optional
safety margin). This is a simplified model:

- Only the end-effector position is checked, not the full swept
  volume of each link.
- No self-collision (arm vs. torso) is modeled, since this project
  only simulates a single arm chain.

## Balance

A simplified model, per the project's original design goals — no
full whole-body controller is implemented:

Center of Mass (COM)
│
Support Polygon (a fixed horizontal range [min_x, max_x])
│
Stable if COM.x falls inside that range


`compute_center_of_mass()` takes a list of joint positions (and
optional per-joint masses; defaults to equal weighting) and returns
the unweighted or weighted average position. `check_balance()`
raises `BalanceViolationError` if the resulting COM x-coordinate
falls outside the given `SupportPolygon`.

## Error types

| Error                     | Raised when |
|----------------------------|-------------|
| `JointLimitError`           | a joint angle falls outside its allowed range |
| `UnreachableTargetError`     | target distance exceeds the arm's total reach |
| `IKConvergenceError`          | IK solver exhausted all starting attempts without converging |
| `CollisionError`               | a trajectory waypoint intersects an obstacle |
| `BalanceViolationError`         | center of mass falls outside the support polygon |