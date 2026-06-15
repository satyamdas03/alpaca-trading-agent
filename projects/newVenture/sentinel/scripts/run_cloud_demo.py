"""Stub cloud demo for Sentinel verifier."""

from __future__ import annotations

import uuid

from sentinel_verifier.models import (
    Footprint,
    Pose2,
    ProposedAction,
    SafetyContext,
    Velocity2,
    WorldState,
)


def build_sample_plan() -> tuple[WorldState, ProposedAction, SafetyContext]:
    world = WorldState(
        robot_id="amr-07",
        pose=Pose2(x=1.0, y=2.0, theta=0.0),
        velocity=Velocity2(vx=0.5),
        footprint=Footprint(type="circle", radius=0.3),
    )
    action = ProposedAction(
        type="trajectory",
        waypoints=[Pose2(x=2.0, y=2.0), Pose2(x=5.0, y=2.0)],
        max_speed=1.5,
        time_horizon=5.0,
    )
    context = SafetyContext(zone="shared_aisle", human_present=True)
    return world, action, context


def main() -> None:
    world, action, context = build_sample_plan()
    plan_id = f"plan_{uuid.uuid4().hex[:12]}"

    print("Sentinel Cloud Demo")
    print("===================")
    print(f"Robot:   {world.robot_id}")
    print(f"Plan:    {plan_id}")
    print(f"Pose:    ({world.pose.x}, {world.pose.y})")
    print(f"Action:  {action.type} with {len(action.waypoints or [])} waypoints")
    print(f"Context: {context.zone}, human_present={context.human_present}")
    print("\nNOTE: Full verifier /verify endpoint is a stub. Checks will be wired in Week 2.")


if __name__ == "__main__":
    main()
