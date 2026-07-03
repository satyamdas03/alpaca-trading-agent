import sys
import math

sys.path.insert(0, "next_level")

import world_building_construction_uncertainty as wbcu


def test_save_and_restore_physics_state():
    """Snapshot must restore object positions and velocities exactly."""
    wbcu.setup_simulation()

    # Snapshot the initial state.
    state = wbcu.save_world_state()

    red_id = wbcu.WORLD_KNOWLEDGE["block_red"]["id"]
    initial_pos, _ = wbcu.p.getBasePositionAndOrientation(red_id)

    # Perturb the red block.
    wbcu.p.resetBasePositionAndOrientation(red_id, [10.0, 10.0, 1.0], [0, 0, 0, 1])

    # Restore and verify.
    wbcu.load_world_state(state)
    restored_pos, _ = wbcu.p.getBasePositionAndOrientation(red_id)

    assert math.isclose(restored_pos[0], initial_pos[0], abs_tol=1e-6)
    assert math.isclose(restored_pos[1], initial_pos[1], abs_tol=1e-6)
    assert math.isclose(restored_pos[2], initial_pos[2], abs_tol=1e-6)

    print("test_save_and_restore_physics_state: PASSED")


def test_save_and_restore_robot_mental_state():
    """Snapshot must restore Python-side held-object / constraint state."""
    wbcu.setup_simulation()

    # Set a fake mental state.
    wbcu.ROBOT_STATE["robot_0"]["held_object_name"] = "block_red"
    wbcu.ROBOT_STATE["robot_0"]["current_constraint"] = 999

    state = wbcu.save_world_state()

    # Mutate mental state.
    wbcu.ROBOT_STATE["robot_0"]["held_object_name"] = None
    wbcu.ROBOT_STATE["robot_0"]["current_constraint"] = None

    wbcu.load_world_state(state)

    assert wbcu.ROBOT_STATE["robot_0"]["held_object_name"] == "block_red"
    assert wbcu.ROBOT_STATE["robot_0"]["current_constraint"] == 999

    print("test_save_and_restore_robot_mental_state: PASSED")


def test_simulate_branch_rejects_collision():
    """A plan that pushes a block far away should be rejected by the rollout."""
    wbcu.setup_simulation()

    # Manually create a plan where robot_0 tries to place red at an invalid location.
    plan = [
        {"function": "pickup", "target": "block_red"},
        {"function": "place_at", "target": "100, 100, 100", "uncertainty": 0.9}
    ]

    ok, failed_step, metrics = wbcu.simulate_branch("robot_0", plan)

    # The rollout should fail because place_at cannot reach that far.
    assert ok is False
    assert failed_step is not None
    print(f"test_simulate_branch_rejects_collision: PASSED (failed at {failed_step})")


if __name__ == "__main__":
    test_save_and_restore_physics_state()
    wbcu.p.disconnect()

    test_save_and_restore_robot_mental_state()
    wbcu.p.disconnect()

    test_simulate_branch_rejects_collision()
    wbcu.p.disconnect()
