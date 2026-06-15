"""FastAPI entrypoint for the Sentinel cloud verifier."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import FastAPI

from sentinel_verifier.models import (
    CheckResult,
    ProposedAction,
    SafetyContext,
    Verdict,
    VerdictResponse,
    WorldState,
)

app = FastAPI(title="Sentinel Verifier", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "sentinel-verifier", "version": "0.1.0"}


@app.post("/v1/verify", response_model=VerdictResponse)
async def verify_plan(
    robot_id: str,
    plan_id: str,
    world_state: WorldState,
    proposed_action: ProposedAction,
    safety_context: SafetyContext | None = None,
) -> VerdictResponse:
    """Stub verifier: returns ALLOW for valid trajectories; placeholder for checks."""
    start = datetime.now(timezone.utc)
    safety_context = safety_context or SafetyContext()

    # Placeholder: always allow until checks are wired in Week 2.
    checks = [
        CheckResult(name="collision_free", result="PASS", detail="stub"),
        CheckResult(name="speed_limit", result="PASS", detail="stub"),
        CheckResult(name="geofence", result="PASS", detail="stub"),
        CheckResult(name="human_proximity", result="PASS", detail="stub"),
    ]

    latency_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000.0

    return VerdictResponse(
        receipt_id=f"recv_{uuid.uuid4().hex[:16]}",
        verdict=Verdict.ALLOW,
        robot_id=robot_id,
        plan_id=plan_id,
        policy_version="v0.0.0-stub",
        checks=checks,
        latency_ms=latency_ms,
    )
