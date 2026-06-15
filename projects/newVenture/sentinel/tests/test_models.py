"""Smoke tests for Sentinel shared models."""

from sentinel_verifier.models import Pose2, ProposedAction, Vector2, Verdict, WorldState


def test_pose2_json_roundtrip() -> None:
    pose = Pose2(x=1.0, y=2.0, theta=0.5)
    data = pose.model_dump()
    restored = Pose2(**data)
    assert restored.x == 1.0
    assert restored.y == 2.0
    assert restored.theta == 0.5


def test_world_state_defaults() -> None:
    world = WorldState(robot_id="test-01", pose=Pose2(x=0, y=0))
    assert world.robot_id == "test-01"
    assert world.velocity.vx == 0.0
    assert world.perception == []


def test_proposed_action_with_waypoints() -> None:
    action = ProposedAction(
        type="trajectory",
        waypoints=[Pose2(x=1, y=1), Pose2(x=2, y=2)],
        max_speed=1.5,
    )
    assert action.type == "trajectory"
    assert len(action.waypoints or []) == 2
    assert (action.waypoints or [])[0].x == 1.0


def test_verdict_enum_values() -> None:
    assert Verdict.ALLOW.value == "ALLOW"
    assert Verdict.HOLD.value == "HOLD"
    assert Verdict.REJECT.value == "REJECT"


def test_vector2() -> None:
    v = Vector2(x=3.0, y=4.0)
    assert v.x == 3.0
    assert v.y == 4.0
