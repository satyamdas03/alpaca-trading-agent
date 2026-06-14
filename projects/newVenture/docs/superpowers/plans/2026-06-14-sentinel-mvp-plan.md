# Sentinel MVP Implementation Plan

**Date:** 2026-06-14  
**Status:** Draft — pending final approval before execution  
**Owner:** Satyam Das + assistant  
**Target demo:** 2026-07-12 (4 weeks from plan approval)

This plan turns the Sentinel design spec into a concrete, week-by-week build sequence. The goal is a **software-only, simulation-first MVP** that proves the three-layer architecture end-to-end with one warehouse AMR + humanoid coexistence scenario.

---

## 1. MVP Definition (What We Are Building)

### 1.1 In Scope

A single, closed-loop demo showing:

1. **Scene Forge** generates a warehouse USD scene with one AMR, one humanoid, static obstacles, and a pedestrian walk path.
2. A simple "planner" (Python script) emits proposed trajectories for both robots.
3. **Sentinel Verifier** receives the proposed trajectories + world state and returns a signed verdict: `ALLOW`, `HOLD`, or `REJECT`.
4. **Verifier Nano** runs the same policy locally on an edge-style binary and returns a verdict even when cloud is unreachable.
5. **Evidence Vault** stores every verdict, scene snapshot, and replay asset in S3 + DynamoDB with a signed receipt.
6. **Command Center** displays live verdict stream, robot state, incident replay, and a safety scorecard.
7. **Policy Forge** (minimal CLI + YAML) lets a user edit geofence, speed, and human-proximity rules and re-verify a plan.

### 1.2 Out of Scope (Explicitly Deferred)

| Item | Why Deferred | When Revisited |
|------|--------------|----------------|
| Real hardware (Jetson, physical AMR) | Software-only MVP. Edge tested as local Linux binary. | Post-demo / paid pilot |
| ROS2/Isaac ROS integration | Adds complexity; simulated trajectories are sufficient for MVP. | Week 5–6 |
| Multi-fleet scheduling optimization | Focus on safety verification, not fleet orchestration. | Phase 2 |
| Formal theorem proving | Lightweight interval + sampling checks only. | Enterprise tier |
| QLDB / blockchain-grade audit | S3 + DynamoDB signed receipts are enough for demo. | Enterprise tier |
| Natural-language policy authoring | CLI/YAML authoring only. | Phase 2 |
| Mobile/native edge apps | Web dashboard only. | Later |

### 1.3 Success Criteria

By end of Week 4, the system must:

- [ ] Run a full verification loop cloud-side in < 500 ms p95.
- [ ] Run Verifier Nano locally in < 50 ms p95.
- [ ] Produce a signed, streamable receipt for every verdict.
- [ ] Replay any `REJECT` incident in the dashboard within 3 clicks.
- [ ] Demonstrate a policy change propagating from Policy Forge → Verifier Nano in < 60 seconds.
- [ ] Operate during a simulated network partition with cached policy.
- [ ] Be deployable on AWS via one IaC command (`cdk deploy` or CloudFormation).

---

## 2. Architecture for MVP

```
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 1: SIMULATION & VERIFICATION FACTORY (AWS Cloud)              │
│  EC2 g6 (Isaac Sim) → Scene Forge → S3/EBS                          │
│  Python Sentinel Verifier (ECS/Fargate) → DynamoDB + S3             │
│  Policy Forge (YAML + small Streamlit/Gradio UI)                    │
└─────────────────────────────────────────────────────────────────────┘
                                           │
                                           │ HTTPS / WebSocket
                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 2: EDGE RUNTIME (Local dev machine as stand-in)                │
│  Verifier Nano (Python + compiled optional Rust/Cython core)          │
│  Edge Telemetry Bridge (MQTT to AWS IoT Core)                         │
│  Actuator Gate (stub; logs instead of moving hardware)                │
└─────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 3: COMMAND CENTER (Web dashboard)                              │
│  Next.js or Streamlit on ECS / S3+CloudFront                         │
│  Cognito auth (optional for MVP; can defer to demo-only)            │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.1 AWS Services Used

| Purpose | Service | Notes |
|---------|---------|-------|
| Simulation host | EC2 g6.xlarge (Isaac Sim) | Spot where possible; 4 h/day dev budget |
| Container registry | ECR | Verifier, dashboard, Policy Forge images |
| Compute | ECS Fargate | Verifier API, dashboard SSR/API routes |
| Edge simulation | Local binary + AWS IoT Core | Greengrass deferred; use direct MQTT for MVP |
| Database | DynamoDB | Verdicts, receipts, policy versions, robot registry |
| Object store | S3 | Scene assets, replay videos, receipt archives |
| Time series | Timestream (optional) | Telemetry buffer; can use DynamoDB TTL stream for MVP |
| Auth | Cognito (optional) | Defer if Streamlit public demo is acceptable |
| CI/CD | GitHub Actions → ECR → ECS | Or AWS CodePipeline if preferred |
| IaC | AWS CDK (Python) | Single `cdk deploy` for repeatable environments |

---

## 3. Repository Structure

```
sentinel/
├── README.md
├── pyproject.toml / requirements.txt
├── cdk/
│   ├── app.py
│   ├── sentinel_stack.py          # VPC, ECS, DynamoDB, S3, IoT Core
│   └── simulation_stack.py        # EC2 Isaac Sim host (optional)
├── packages/
│   ├── scene_forge/
│   │   ├── __init__.py
│   │   ├── generators.py          # USD warehouse + AMR + humanoid
│   │   ├── exporters.py           # world_state.json + occupancy grid
│   │   └── assets/                # USD primitives, textures
│   ├── sentinel_verifier/
│   │   ├── __init__.py
│   │   ├── api.py                 # FastAPI app
│   │   ├── models.py              # Pydantic: WorldState, Plan, Verdict
│   │   ├── checks/
│   │   │   ├── geofence.py
│   │   │   ├── collision.py
│   │   │   ├── speed.py
│   │   │   └── human_proximity.py
│   │   ├── policy.py              # Policy loader + version hash
│   │   ├── receipt.py             # Sign + serialize receipts
│   │   └── tests/
│   ├── verifier_nano/
│   │   ├── __init__.py
│   │   ├── nano.py                # Minimal local verifier
│   │   ├── cache.py               # Policy + receipt cache
│   │   └── bridge.py              # MQTT publish/subscribe
│   ├── edge_telemetry/
│   │   ├── __init__.py
│   │   └── mock_robot.py          # Publishes AMR/humanoid state
│   ├── policy_forge/
│   │   ├── __init__.py
│   │   ├── templates.yaml
│   │   ├── policy_schema.json
│   │   └── ui.py                  # Streamlit policy editor
│   └── command_center/
│       ├── frontend/              # Next.js or Streamlit
│       └── backend/
│           └── sentinel_api_client.py
├── scenarios/
│   └── warehouse_coexistence_v1.json
├── policies/
│   └── warehouse_default_v1.yaml
└── scripts/
    ├── run_cloud_demo.py
    ├── run_edge_demo.py
    └── render_replay.py
```

---

## 4. Week-by-Week Build Sequence

### Week 1: Simulation Foundation & Scene Forge

**Theme:** We can build and inspect a realistic warehouse scene, and extract a structured world state from it.

#### Week 1 Goals

- [ ] Isaac Sim 4.x running headless on EC2 g6.xlarge (or local RTX machine if available sooner).
- [ ] Scene Forge can generate a warehouse USD with:
  - 4 rack rows, 1 loading dock, 1 pedestrian corridor.
  - 1 AMR (DiffDrive) + 1 humanoid (tall capsule / placeholder model).
  - Walk path waypoints for a human worker.
- [ ] Export `world_state.json` containing:
  - Static obstacles (AABB boxes).
  - Robot poses, velocities, footprints.
  - Humanoid skeleton/pose stub.
- [ ] Basic replay renderer: save MP4 of a trajectory from Isaac Sim.
- [ ] Repository scaffold + `pyproject.toml` + initial tests.
- [ ] AWS CDK skeleton creates VPC + S3 + DynamoDB.

#### Week 1 Tasks (Day-by-Day)

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| Mon | Create repo layout, `pyproject.toml`, CI lint/test | Assistant | PR merged |
| Tue | Stand up Isaac Sim on EC2 g6; document install + license | Satyam | SSH access confirmed |
| Wed | Build Scene Forge USD generator for racks + dock | Assistant | `warehouse_basic.usd` |
| Thu | Add AMR + humanoid actors + walk path; export world_state.json | Satyam | JSON schema valid |
| Fri | Implement replay renderer; write first unit tests | Assistant | 5+ passing tests |
| Sat | AWS CDK: VPC, S3, DynamoDB tables | Satyam | `cdk synth` clean |
| Sun | Buffer / documentation / Isaac Sim troubleshooting | Both | Week 1 report |

#### Week 1 Exit Risks

- **Isaac Sim licensing/driver issues on EC2.** Mitigation: use local RTX workstation as fallback; switch to Gazebo/MuJoCo only if absolutely necessary.
- **USD export format confusion.** Mitigation: pin Isaac Sim 4.x and use official Python snippets.

---

### Week 2: Cloud Verifier & Evidence Vault

**Theme:** Any proposed plan can be submitted to a cloud API and receive a signed verdict with a full audit trail.

#### Week 2 Goals

- [ ] FastAPI `Sentinel Verifier` service with `/verify` endpoint.
- [ ] Pydantic models: `WorldState`, `RobotPlan`, `Policy`, `Verdict`, `Receipt`.
- [ ] Four invariant checks implemented:
  - Geofence boundary.
  - Static obstacle collision (AABB/footprint sweep).
  - Speed envelope per robot class.
  - Human proximity / shared-zone timeout.
- [ ] Policy loader with version hash and signature.
- [ ] Receipt generator: JSON receipt + SHA-256 hashes + Ed25519 signature stub.
- [ ] Evidence Vault: S3 stores replay MP4 + scene snapshot; DynamoDB stores receipt metadata.
- [ ] Policy Forge CLI + YAML templates.
- [ ] Containerize verifier and push to ECR; deploy to ECS Fargate.

#### Week 2 Tasks

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| Mon | Define Pydantic models + FastAPI skeleton | Assistant | `/health` returns OK |
| Tue | Implement geofence + collision checks + tests | Satyam | 10+ unit tests green |
| Wed | Implement speed + human-proximity checks | Assistant | edge cases documented |
| Thu | Policy loader + version hashing; Policy Forge YAML | Satyam | `policies/warehouse_default_v1.yaml` |
| Fri | Receipt generator + Evidence Vault (S3/DynamoDB) | Assistant | sample receipt signed + stored |
| Sat | Dockerize verifier; ECR; ECS Fargate via CDK | Satyam | cloud endpoint callable |
| Sun | Buffer / integration tests / docs | Both | Week 2 report |

#### Week 2 Exit Risks

- **Collision math too slow.** Mitigation: use coarse AABB first, then circle-sphere sweep; accept sampling-based approximation for MVP.
- **S3/DynamoDB permissions complexity.** Mitigation: CDK grants least-privilege roles; test with IAM simulator.

---

### Week 3: Edge Verifier Nano & Telemetry Bridge

**Theme:** The same policy can run on a lightweight local verifier, survive network loss, and stream telemetry to the cloud.

#### Week 3 Goals

- [ ] `verifier_nano` Python module replicates cloud checks on a single trajectory.
- [ ] Policy cache: load policy from local file; update via MQTT/HTTPS.
- [ ] Fail-safe defaults: missing policy → `HOLD`; missing telemetry → `HOLD`.
- [ ] Edge Telemetry Bridge: mock robot publishes pose + plan to AWS IoT Core via MQTT.
- [ ] Verdicts from edge are uploaded to DynamoDB when online.
- [ ] Simulate network partition: Verifier Nano continues with cached policy; queues receipts.
- [ ] Latency benchmark: cloud < 500 ms, nano < 50 ms.

#### Week 3 Tasks

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| Mon | Port core checks to `verifier_nano`; no Isaac dependency | Assistant | local tests pass |
| Tue | Policy cache + update mechanism | Satyam | policy swap in < 60 s |
| Wed | Mock robot telemetry publisher + MQTT bridge | Assistant | IoT Core receives messages |
| Thu | Edge verdict upload + offline queue | Satyam | partition test passes |
| Fri | Latency benchmarks + optimization pass | Assistant | benchmark report |
| Sat | End-to-end loop: mock robot → nano → cloud → dashboard stub | Both | first full run |
| Sun | Buffer / security review of MQTT topics | Both | Week 3 report |

#### Week 3 Exit Risks

- **IoT Core policy misconfiguration.** Mitigation: use CDK to generate thing certificates; test with AWS CLI first.
- **Latency over 50 ms in Python.** Mitigation: profile with py-spy; rewrite hot path in Rust/Cython if needed.

---

### Week 4: Command Center Dashboard & Demo Hardening

**Theme:** A non-technical buyer can open a dashboard, see live safety status, and replay a near-miss in under 60 seconds.

#### Week 4 Goals

- [ ] Command Center frontend (Next.js or Streamlit) with:
  - Fleet status panel: robot cards, online/offline, last verdict.
  - Verdict stream: real-time table with filters.
  - Incident replay: load S3 replay + overlay verdict + world state.
  - Safety scorecard: violation counts, policy version coverage, latency p95.
- [ ] Backend API routes: `/robots`, `/verdicts`, `/receipts/:id`, `/replay/:id`.
- [ ] Demo scenario script: generate 3 intentional violations (geofence breach, collision course, human too close).
- [ ] Deployment pipeline: GitHub Actions builds ECR images on push to `main`.
- [ ] Runbook + demo script + 1-minute elevator pitch.
- [ ] Cost estimate and teardown instructions.

#### Week 4 Tasks

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| Mon | Scaffold dashboard frontend + API client | Assistant | hello-world page |
| Tue | Fleet status + verdict stream panels | Satyam | real data flowing |
| Wed | Incident replay panel + S3 presigned URLs | Assistant | replay loads in dashboard |
| Thu | Safety scorecard + latency chart | Satyam | demo-ready metrics |
| Fri | Build 3 violation scenarios + demo script | Assistant | repeatable demo |
| Sat | GitHub Actions CI/CD + final deploy | Satyam | `main` auto-deploys |
| Sun | Dress rehearsal, docs, runbook | Both | demo video / live call |

#### Week 4 Exit Risks

- **Dashboard too complex for one week.** Mitigation: use Streamlit if Next.js slips; polish in Phase 2.
- **Demo unstable.** Mitigation: record a 90-second demo video as backup.

---

## 5. Interfaces & Data Contracts

### 5.1 `/verify` Endpoint (Cloud)

```python
POST /v1/verify
Headers: X-Sentinel-Policy-Version: v1.3.2
Body:
{
  "robot_id": "amr-07",
  "plan_id": "plan_...",
  "world_state": { ... },
  "proposed_plan": { ... }
}
Response:
{
  "receipt_id": "recv_...",
  "verdict": "ALLOW" | "HOLD" | "REJECT",
  "checks": [...],
  "policy_version": "v1.3.2",
  "signature": "ed25519:...",
  "timestamp_utc": "..."
}
```

### 5.2 Verdict Semantics

| Verdict | Meaning | Default Action |
|---------|---------|----------------|
| `ALLOW` | All checks passed within tolerance. | Execute plan. |
| `HOLD`  | Insufficient data, policy stale, or marginal risk. | Pause / request human review. |
| `REJECT`| Definite violation or safety-critical failure. | Emergency stop / do not execute. |

### 5.3 MQTT Topics (Edge)

```
sentinel/robots/{robot_id}/telemetry      → cloud
sentinel/robots/{robot_id}/plan            → edge verifier input
sentinel/robots/{robot_id}/verdict         → cloud upload
sentinel/policies/{policy_version}/update   → edge policy update
```

### 5.4 DynamoDB Tables

| Table | Hash Key | Sort Key | Purpose |
|-------|----------|----------|---------|
| `SentinelRobots` | `robot_id` | `timestamp` | Registry + latest state |
| `SentinelVerdicts` | `robot_id` | `receipt_id` | Verdict metadata + index |
| `SentinelReceipts` | `receipt_id` | - | Full signed receipt |
| `SentinelPolicies` | `policy_version` | - | Policy JSON + hash |

### 5.5 S3 Buckets

| Bucket | Prefixes |
|--------|----------|
| `sentinel-evidence-{account}-{region}` | `scenes/`, `replays/`, `receipts/`, `policies/` |

---

## 6. Testing Strategy

### 6.1 Unit Tests

- Geometry primitives (AABB, distance, sweep).
- Each invariant check with positive and negative cases.
- Policy loader + version hash.
- Receipt signature round-trip.
- Verdict Nano parity with cloud verifier (same input → same verdict).

### 6.2 Integration Tests

- Scene Forge → world_state.json schema validation.
- `/verify` HTTP round-trip with sample plan.
- Evidence Vault write → DynamoDB + S3 read-back.
- Edge bridge MQTT publish → cloud verdict upload.
- Network partition simulation.

### 6.3 Demo / Smoke Tests

- `run_cloud_demo.py`: generates a violation, calls `/verify`, prints receipt.
- `run_edge_demo.py`: runs Verifier Nano with mock robot for 60 seconds.
- Dashboard opens and shows live verdict stream for > 5 minutes.

---

## 7. Security & Safety Defaults

- **Fail-safe:** Any exception, timeout, or missing required field returns `HOLD` or `REJECT`, never `ALLOW`.
- **Policy immutability:** Every policy version has a SHA-256 hash; receipts reference the hash.
- **Signature stub:** Ed25519 key generated per deployment; production moves to KMS/HSM.
- **Least privilege:** CDK roles scoped to required actions only.
- **No PII:** Demo uses synthetic robot IDs and fake facility coordinates.
- **IoT TLS:** MQTT over TLS 1.2+ with certificate-based auth.

---

## 8. Cost Estimate (4 Weeks, US East)

| Resource | Spec | Hours/Day | Monthly ~ |
|----------|------|-----------|-----------|
| EC2 Isaac Sim | g6.xlarge Spot | 4 h | $150–250 |
| ECS Fargate verifier | 1 vCPU / 2 GB | 24 h | $40–60 |
| ECS Fargate dashboard | 0.5 vCPU / 1 GB | 24 h | $20–30 |
| DynamoDB on-demand | small traffic | — | $5–15 |
| S3 | < 10 GB assets | — | $1–5 |
| IoT Core | < 1M messages | — | $1–5 |
| ECR | 4 images | — | $5–10 |
| Data transfer | modest | — | $10–20 |
| **Total** | | | **~$250–400 for the month** |

Use Spot, teardown non-prod stacks nightly, and use a single ECS task for verifier+dashboard if costs need tightening.

---

## 9. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Isaac Sim setup takes > 3 days | Medium | High | Fallback to local RTX; pre-build AMI; use Isaac Sim Docker |
| Cloud verifier latency > 500 ms | Medium | Medium | Add coarse AABB; cache world state; profile with py-spy |
| Edge verifier too slow in pure Python | Low | Medium | Rust/Cython rewrite only if benchmark fails |
| CDK/IAM permission bugs slow deploy | High | Medium | Use least-privilege from day 1; test with IAM simulator |
| Dashboard slips past Week 4 | Medium | High | Streamlit fallback; pre-record demo video |
| No customer feedback until demo | High | High | Schedule 2–3 warehouse/robotics intro calls in Week 2–3 |

---

## 10. Open Questions to Resolve in Week 1

1. **Isaac Sim license:** Do we have an active NVIDIA Omniverse account? If not, create immediately.
2. **AWS account / credits:** Confirm account ID, region, and available credits/budget.
3. **Local hardware:** Is there an RTX-class local machine we can use as Isaac Sim dev host before EC2 is ready?
4. **Dashboard tech:** Next.js (better for investors) or Streamlit (faster to build)? Decide by end of Week 1.
5. **Real customer intro:** Who are the first 3 warehouse/AMR/humanoid contacts we can demo to? Schedule in Week 2.

---

## 11. Definition of Done (MVP Complete)

The MVP is complete when:

1. `cdk deploy` creates the full AWS environment.
2. `run_cloud_demo.py` produces an `ALLOW` and a `REJECT` receipt.
3. `run_edge_demo.py` runs Verifier Nano for 60 s with at least one cached-policy verdict.
4. Command Center displays live verdicts for both cloud and edge runs.
5. Incident replay loads from S3 and shows the violation frame.
6. Demo script is rehearsed and can be delivered in 8 minutes.
7. All code is committed, linted, and has passing tests in CI.

---

## 12. Next Step

**Approve this plan to begin Week 1 execution.**

Once approved, the first actions will be:
1. Create the Sentinel repository and scaffold.
2. Open an NVIDIA Omniverse / Isaac Sim account.
3. Confirm AWS account + region + budget.
4. Begin the CDK skeleton (VPC, S3, DynamoDB).
