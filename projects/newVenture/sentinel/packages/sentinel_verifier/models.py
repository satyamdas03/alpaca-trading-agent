"""Shared Pydantic models for Sentinel cloud and edge verifiers."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Vector2(BaseModel):
    x: float
    y: float


class Pose2(BaseModel):
    x: float
    y: float
    theta: float = 0.0
    frame: str = "map"


class Velocity2(BaseModel):
    vx: float = 0.0
    vy: float = 0.0
    omega: float = 0.0


class Footprint(BaseModel):
    """Convex polygon or circle approximation in robot-local frame."""

    type: Literal["circle", "polygon"] = "circle"
    radius: float | None = None
    vertices: list[Vector2] | None = None


class WorldState(BaseModel):
    robot_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pose: Pose2
    velocity: Velocity2 = Field(default_factory=Velocity2)
    footprint: Footprint = Field(default_factory=lambda: Footprint(type="circle", radius=0.3))
    perception: list[str] = Field(default_factory=list)


class ProposedAction(BaseModel):
    type: Literal["trajectory", "velocity_command", "emergency_stop"]
    waypoints: list[Pose2] | None = None
    max_speed: float | None = None
    time_horizon: float = 5.0


class SafetyContext(BaseModel):
    zone: str = "default"
    human_present: bool = False
    payload_mass: float = 0.0


class CheckResult(BaseModel):
    name: str
    result: Literal["PASS", "FAIL", "SKIP"]
    detail: str = ""


class Verdict(str, Enum):
    ALLOW = "ALLOW"
    HOLD = "HOLD"
    REJECT = "REJECT"


class VerdictResponse(BaseModel):
    receipt_id: str
    verdict: Verdict
    robot_id: str
    plan_id: str
    policy_version: str
    checks: list[CheckResult]
    timestamp_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float
    signature: str | None = None
    replay_url: str | None = None

    model_config: dict[str, Any] = {"json_encoders": {datetime: lambda v: v.isoformat()}}
