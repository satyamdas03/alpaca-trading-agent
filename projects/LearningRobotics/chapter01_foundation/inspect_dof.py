"""
Chapter 1 — Practical: Load robots, identify joints, count degrees of freedom.

Demonstrates:
  * Configuration = joint angles (qpos)
  * DOF = number of independent joints
  * Joint space -> task space via forward kinematics (end-effector site position)
  * C-space as the torus for revolute joints (angles wrap around)
"""
import math
import numpy as np
import mujoco


def load_model(xml_path: str):
    """Load a MuJoCo model from an XML file."""
    with open(xml_path, "r", encoding="utf-8") as f:
        xml = f.read()
    return mujoco.MjModel.from_xml_string(xml)


def describe_robot(model: mujoco.MjModel, data: mujoco.MjData, name: str):
    """Print joint/DOF/configuration summary for a robot."""
    print("=" * 70)
    print(f"Robot: {name}")
    print("=" * 70)

    nq = model.nq  # configuration-space dimension = number of qpos values
    nv = model.nv  # velocity-space dimension = independent DOF (for this chapter, nv == DOF)
    njoints = model.njnt

    print(f"Total joints (MuJoCo count) : {njoints}")
    print(f"Configuration dimension nq  : {nq}  <- each qpos value is one coordinate in C-space")
    print(f"Velocity DOF nv               : {nv}  <- independent ways the robot can move")
    print(f"End-effector site             : {mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_SITE, model.nsite - 1)}")
    print()

    print("Joints (name | type | axis | qpos index | range [rad]):")
    for jnt_id in range(njoints):
        jnt_name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, jnt_id)
        jnt_type = model.jnt_type[jnt_id]
        type_str = {
            mujoco.mjtJoint.mjJNT_FREE: "free (6 DOF)",
            mujoco.mjtJoint.mjJNT_BALL: "ball (3 DOF)",
            mujoco.mjtJoint.mjJNT_SLIDE: "prismatic",
            mujoco.mjtJoint.mjJNT_HINGE: "revolute",
        }.get(jnt_type, f"unknown({jnt_type})")
        qpos_adr = model.jnt_qposadr[jnt_id]
        axis = model.jnt_axis[jnt_id]
        range_low, range_high = model.jnt_range[jnt_id]
        print(f"  {jnt_id+1}. {jnt_name:12s} | {type_str:12s} | axis={axis} | qpos[{qpos_adr}] | "
              f"[{range_low:+.2f}, {range_high:+.2f}]")
    print()

    # Default configuration end-effector position.
    mujoco.mj_resetData(model, data)
    mujoco.mj_forward(model, data)
    ee_id = model.nsite - 1
    ee_default = data.site_xpos[ee_id].copy()
    print(f"Default config end-effector (task space) : {ee_default}")
    print(f"Default config qpos (C-space point)        : {data.qpos.copy()}")
    print()


def forward_kin_2r(q1: float, q2: float, L1: float = 1.0, L2: float = 0.8):
    """Analytical forward kinematics for the simple 2R planar arm."""
    x = L1 * math.cos(q1) + L2 * math.cos(q1 + q2)
    y = L1 * math.sin(q1) + L2 * math.sin(q1 + q2)
    return np.array([x, y])


def demo_2r_arm():
    print("\n" + "=" * 70)
    print("DEMO: 2R planar arm — joint space -> task space")
    print("=" * 70)

    model = load_model("simple_2r_arm.xml")
    data = mujoco.MjData(model)
    describe_robot(model, data, "simple_2r_arm.xml (2 revolute joints)")

    ee_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "ee")
    configs = [
        ("elbow straight out", np.array([0.0, 0.0])),
        ("raised 45 deg", np.array([math.radians(45), 0.0])),
        ("bent 90 deg", np.array([0.0, math.radians(90)])),
        ("full reach", np.array([0.0, math.radians(180)])),
    ]

    print(f"{'Description':20s} | {'qpos (joint space)':>30s} | {'MuJoCo FK (x,y)':>24s} | {'Analytical FK (x,y)':>24s}")
    print("-" * 105)
    for desc, qpos in configs:
        data.qpos[:] = qpos
        mujoco.mj_forward(model, data)
        mujoco_fk = data.site_xpos[ee_id][:2]
        analytic_fk = forward_kin_2r(qpos[0], qpos[1])
        print(f"{desc:20s} | [{qpos[0]:+.3f}, {qpos[1]:+.3f}] | "
              f"({mujoco_fk[0]:+.3f}, {mujoco_fk[1]:+.3f}) | "
              f"({analytic_fk[0]:+.3f}, {analytic_fk[1]:+.3f})")
    print()


def demo_6dof_arm():
    print("\n" + "=" * 70)
    print("DEMO: 6-DOF spatial arm — 6 revolute joints match 6-DOF task space")
    print("=" * 70)

    model = load_model("simple_6dof_arm.xml")
    data = mujoco.MjData(model)
    describe_robot(model, data, "simple_6dof_arm.xml (6 revolute joints)")

    ee_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "ee")
    configs = [
        ("all zeros", np.zeros(6)),
        ("waist 90 deg", np.array([math.radians(90), 0, 0, 0, 0, 0])),
        ("shoulder raised", np.array([0, math.radians(45), 0, 0, 0, 0])),
        ("wrist pitch", np.array([0, 0, 0, 0, math.radians(45), 0])),
    ]

    print(f"{'Description':18s} | {'qpos (joint space/C-space)':>55s} | {'End-effector (x,y,z)':>30s}")
    print("-" * 110)
    for desc, qpos in configs:
        data.qpos[:] = qpos
        mujoco.mj_forward(model, data)
        ee_pos = data.site_xpos[ee_id]
        q_str = ", ".join(f"{v:+.2f}" for v in qpos)
        print(f"{desc:18s} | [{q_str}] | ({ee_pos[0]:+.3f}, {ee_pos[1]:+.3f}, {ee_pos[2]:+.3f})")
    print()


def demo_cspace_topology():
    print("\n" + "=" * 70)
    print("DEMO: C-space topology — revolute joints live on a circle")
    print("=" * 70)
    print("For one revolute joint: q = 0 rad and q = 2*pi rad are the SAME pose.")
    print("So the C-space of one revolute joint is a circle (S^1), not a line.")
    print("Two revolute joints -> C-space is a torus (S^1 x S^1).")
    print()

    model = load_model("simple_2r_arm.xml")
    data = mujoco.MjData(model)
    ee_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, "ee")

    for q1 in [0.0, 2 * math.pi, 4 * math.pi]:
        for q2 in [0.0, 2 * math.pi]:
            data.qpos[:] = [q1, q2]
            mujoco.mj_forward(model, data)
            ee = data.site_xpos[ee_id][:2]
            print(f"q1={q1:+.4f}, q2={q2:+.4f} -> ee=({ee[0]:+.4f}, {ee[1]:+.4f})")
    print()


def main():
    demo_2r_arm()
    demo_6dof_arm()
    demo_cspace_topology()
    print("=" * 70)
    print("Chapter 1 practical complete.")
    print("Key takeaway: joint angles = configuration = a point in C-space.")
    print("Changing that point moves the end-effector through task space.")
    print("=" * 70)


if __name__ == "__main__":
    main()
