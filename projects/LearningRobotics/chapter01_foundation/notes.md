# Chapter 1 — Foundations, Configuration Space & DOF

**Date:** 2026-08-13  
**Setup:** Lenovo LOQ, RTX 5060, NVIDIA driver 595.95, CUDA 13.2, Python 3.11 venv, MuJoCo 3.11.0  
**Goal:** Install a robot simulator, load robots, identify joints, and count DOF.

## What we did

Installed MuJoCo inside a Python 3.11 virtual environment. Used two custom minimal robot models to make the concepts explicit:

1. `simple_2r_arm.xml` — two revolute joints in a plane (2 DOF). Demonstrates that:
   * Configuration = `(q1, q2)` = a point in a 2-D C-space.
   * Each joint angle maps to one coordinate in C-space.
   * Forward kinematics converts the C-space point to a task-space point `(x, y)`.
   * MuJoCo FK matches analytical FK exactly.

2. `simple_6dof_arm.xml` — six revolute joints in 3D (6 DOF). Demonstrates that:
   * Six independent joint angles give six independent ways to move.
   * This matches the 6 DOF of a free rigid body in 3D (3 position + 3 orientation).
   * A 6-DOF serial arm is the standard industrial design.

## Key numbers observed

| Robot | Joints | DOF (`nv`) | C-space dimension (`nq`) | End-effector default (task space) |
|-------|--------|-----------|-------------------------|-----------------------------------|
| 2R planar arm | 2 revolute | 2 | 2 | (1.800, 0.000, 0.050) |
| 6-DOF spatial arm | 6 revolute | 6 | 6 | (0.960, 0.000, 0.850) |

## C-space topology

* A revolute joint’s angle wraps around: `0` and `2π` are the same pose.
* Therefore a single revolute joint has a **circle** (`S^1`) as its C-space, not a line.
* Two revolute joints together have a **torus** (`S^1 × S^1`) as their C-space.

## Joint-space → task-space evidence

2R arm, analytical vs MuJoCo forward kinematics:

| Configuration | Analytical (x, y) | MuJoCo FK (x, y) |
|---------------|-------------------|------------------|
| `(0, 0)` | (1.800, 0.000) | (1.800, 0.000) |
| `(π/4, 0)` | (1.273, 1.273) | (1.273, 1.273) |
| `(0, π/2)` | (1.000, 0.800) | (1.000, 0.800) |
| `(0, π)` | (0.200, 0.000) | (0.200, 0.000) |

## Isaac Sim note

Isaac Sim was not installed in this session. The chapter suggests it as the heavier target simulator; MuJoCo was chosen for instant feedback and because it runs cleanly on the RTX 5060 without a multi-gigabyte download. The concepts transfer 100% — when we reach RL chapters we can revisit Isaac Lab / Isaac Sim.

## Command to rerun

```powershell
cd chapter01_foundation
. .venv\Scripts\Activate.ps1
python inspect_dof.py
```

## Next chapter

Chapter 2 — Rigid-Body Motions: coordinate frames, rotations, and homogeneous transformations.
