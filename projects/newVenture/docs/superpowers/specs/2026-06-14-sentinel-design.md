# Sentinel — Runtime Safety for Physical AI

**Design Spec** · `2026-06-14` · Status: Approved pending user review of written spec

---

## 1. Overview

**Product name:** Sentinel  
**Tagline:** Verified Physical AI — runtime safety for robots, drones, and autonomous machines.  
**One-liner:** Sentinel is an AWS-native runtime safety service that verifies every AI-generated robot action against physics and safety invariants in simulation before deployment, then continues verifying live actions at the edge after deployment.

**Strategic goal:** Build a software-only, AWS-native, simulation-first safety verifier for physical AI, demonstrate it with warehouse AMR/humanoid fleet safety, and position it for acquisition by a robotics OEM, autonomy prime, or AI safety platform.

**No hardware dependency.** The MVP runs entirely in AWS cloud simulation. Production runtime deploys to customer edge hardware via AWS IoT Greengrass.

---

## 2. Problem Statement

The world is deploying physical AI faster than it can verify it. Robots, drones, and autonomous vehicles now use black-box AI models to plan actions in dynamic environments. A bad action in the physical world is not a chatbot embarrassment — it is a collision, injury, liability, or program cancellation.

Current safety approaches are insufficient:
- **Reactive sensors** detect danger after it appears.
- **Simulation suites** test scenarios but do not authorize live actions.
- **OEM safety stacks** are vendor-locked and not model-agnostic.
- **Academic safety filters** (CBF, Simplex) are not packaged as products.

There is no independent, model-agnostic, physics-aware runtime verifier that proves an action is safe before a machine executes it and produces audit-grade evidence.

---

## 3. Market Context

### Market signals
- Physical AI funding hit **$13.8B in 2025** (up 77% YoY).
- **Skild AI** valued at **$14B** (Jan 2026).
- **Anduril** at **$61B valuation** (May 2026).
- **Saronic** at **$9.25B valuation** (March 2026).
- **NVIDIA Halos** announced as full-stack safety system for Physical AI (GTC 2026).
- ISO/TC 299 developing new robotics safety standards (ISO/WD 25874.2, humanoid WG12).

### Segment sizes (2026)
| Segment | 2026 Size | CAGR |
|---|---|---|
| Robot Safety Monitoring AI | $2.66B | 17.5% |
| Autonomous Construction Equipment | $18.16B | 9.2% |
| AI Governance Platforms | $492M | >20% |
| Autonomous Tractors / Ag Robotics | $2.0–$2.7B | ~22% |
| Surgical Robotics | Multi-billion | Mid-teens |

### Acquisition heat (2026)
- Mobileye → Mentee Robotics (~$900M)
- Meta → ARI (humanoid foundation models)
- Amazon → Rivr, Fauna Robotics
- OpenAI → Promptfoo (AI security/red-teaming)
- Anthropic → Vercept (AI computer use)
- ABB → Sevensense, Meshmind
- SoftBank → ABB Robotics ($5.375B)
- Locus Robotics → Nexera Robotics

---

## 4. Target Customer

### Primary beachhead
**Warehouse / logistics AMR + humanoid fleet safety**

Focus on coexistence, collision avoidance, geofence, speed envelope, and stability — not manipulation. Fleet coexistence is robot-vendor-agnostic, urgent, and software-buyable.

### Buyer personas
1. **VP of Autonomy / Head of Robotics Engineering** — primary buyer, owns robot deployment.
2. **Head of Safety / Regulatory Affairs** — needs audit-grade evidence.
3. **Corp Dev / CTO at OEM or autonomy prime** — strategic acquirer.

### Why this beachhead first
- Fastest to validate in simulation.
- Lower liability than drones or surgery.
- Direct software budget.
- Broad applicability across AMR vendors and humanoid deployers.

---

## 5. Architecture

### Three-layer design

```
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 1: SIMULATION & VERIFICATION FACTORY (AWS Cloud)              │
│  Scene Forge → Planner Adapter → Sentinel Verifier → Evidence Vault │
│  Policy Forge (constraint authoring + templates)                    │
└─────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 2: EDGE RUNTIME (AWS IoT Greengrass / Jetson / x86)            │
│  Sensor Fusion → Edge Planner → Verifier Nano → Actuator Gate       │
└─────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 3: COMMAND CENTER (AWS-Hosted Dashboard)                       │
│  Fleet status · Verdict stream · Incident replay · Safety reports     │
└─────────────────────────────────────────────────────────────────────┘
```

### AWS service stack
| Function | AWS Service |
|---|---|
| GPU simulation | EC2 g5/g6 + NVIDIA Isaac Sim container |
| Scenario orchestration | AWS Batch / Step Functions |
| Verifier compute | ECS Fargate or EKS |
| Edge deployment | AWS IoT Greengrass |
| Robot telemetry | AWS IoT Core (MQTT) |
| Policy storage | DynamoDB + S3 |
| Dashboard hosting | CloudFront + S3 + AppSync + Lambda@Edge |
| Time-series verdicts | Amazon Timestream |
| Audit / signed receipts | S3 + DynamoDB (+ QLDB optional) |
| CI/CD | CodePipeline + ECR |
| Auth / API keys | API Gateway + Cognito |

### Simulation engine
**NVIDIA Isaac Sim 4.2** for buyer credibility and NVIDIA ecosystem alignment. The core verifier is simulation-engine-agnostic and can also plug into Gazebo or MuJoCo.

---

## 6. Components

| Component | Layer | Responsibility |
|---|---|---|
| **Scene Forge** | Cloud | Generate parameterized warehouse scenarios with physics ground truth |
| **Planner Adapter** | Cloud | Normalize customer planner output into standard action representation |
| **Sentinel Verifier** | Cloud | Evaluate proposed actions against physics and safety invariants |
| **Policy Forge** | Cloud | Author, version, and store safety policies and invariant templates |
| **Verifier Nano** | Edge | Lightweight on-device verifier running in <50 ms |
| **Edge Telemetry Bridge** | Edge | Ingest robot state, plans, and sensor data |
| **Command Center** | Cloud | Dashboard, replay, reports, policy OTA |
| **Evidence Vault** | Cloud | Signed, immutable verdict receipts |

---

## 7. Interfaces

### Input: proposed action
```json
{
  "robot_id": "amr-07",
  "plan_id": "plan-uuid",
  "timestamp": "2026-06-14T09:23:17Z",
  "world_state": {
    "pose": {"x": 1.2, "y": 3.4, "theta": 0.78, "frame": "map"},
    "velocity": {"vx": 0.5, "vy": 0.0, "omega": 0.1},
    "perception": ["human_1", "pallet_3", "forklift_2"]
  },
  "proposed_action": {
    "type": "trajectory",
    "waypoints": [...],
    "max_speed": 1.5,
    "time_horizon": 5.0
  },
  "safety_context": {
    "zone": "shared_aisle",
    "human_present": true,
    "payload_mass": 50.0
  }
}
```

### Output: verdict + receipt
```json
{
  "verdict": "ALLOW",
  "confidence": 0.94,
  "checks": [
    {"name": "collision_free", "result": "PASS", "detail": "min_distance 0.42m > threshold 0.30m"},
    {"name": "speed_limit", "result": "PASS", "detail": "max_speed 1.2 m/s < 1.5 m/s"},
    {"name": "stability", "result": "PASS", "detail": "CoM within support polygon"}
  ],
  "receipt_id": "recv-uuid",
  "signature": "...",
  "policy_version": "v1.3.2",
  "simulated_in": "isaac-sim-4.2",
  "latency_ms": 23
}
```

### Verdict semantics
| Verdict | Meaning | Robot behavior |
|---|---|---|
| **ALLOW** | All invariants satisfied | Execute action as planned |
| **HOLD** | Invariant marginally violated or uncertainty too high | Pause; request replan or human review |
| **REJECT** | Hard invariant violation | Abort action; execute safe fallback |

### Latency targets
| Layer | Target |
|---|---|
| Cloud verifier | <500 ms (validation, not live control) |
| Edge verifier | <50 ms (live control loop) |
| Receipt streaming | Async, 100–500 ms tolerance |

---

## 8. Pre-built Invariant Templates

1. **Geofence** — robot stays inside authorized zone.
2. **Collision-free** — minimum distance to static and dynamic obstacles above threshold.
3. **Speed envelope** — velocity bounded by zone, payload, and human presence.
4. **Stability** — center of mass inside support polygon with tip-over margin.
5. **Emergency stop** — e-stop signal overrides all actions.
6. **Human proximity** — reduced speed / wider clearance near humans.

---

## 9. Data Flow

### Cloud verification flow
1. User selects invariants in Policy Forge.
2. Scene Forge generates parameterized warehouse scenarios.
3. Planner Adapter feeds world state to customer's AI planner.
4. Planner proposes a trajectory.
5. Sentinel Verifier forward-simulates and evaluates invariants.
6. Evidence Vault stores signed receipt.
7. Command Center shows pass/fail rates and replay.
8. Verified policy bundle is exported to edge runtime.

### Edge runtime flow
1. Robot sensors feed ROS2/Isaac ROS.
2. Edge Telemetry Bridge normalizes state and publishes to AWS IoT Core.
3. Customer's edge planner proposes a trajectory.
4. Verifier Nano loads policy bundle from Greengrass.
5. Verifier Nano checks trajectory against lightweight invariants.
6. Actuator gate executes only ALLOW actions.
7. Receipts stream to Evidence Vault for audit.

### Error handling
- Verifier crash/timeout → default to HOLD or REJECT (fail-safe).
- Missing sensor data → inflate uncertainty bounds; downgrade to HOLD if exceeded.
- Policy mismatch → edge version wins; cloud flags drift.
- Network partition → Verifier Nano runs autonomously with cached policy; receipts queued and flushed on reconnect.
- Invalid action format → Planner Adapter returns structured error, no verdict issued.

---

## 10. Evidence Vault

Every verdict produces a signed receipt:

```json
{
  "receipt_id": "recv_...",
  "robot_id": "amr-07",
  "plan_id": "plan_...",
  "policy_version": "v1.3.2",
  "verdict": "ALLOW",
  "checks": [...],
  "world_state_hash": "sha256:...",
  "proposed_action_hash": "sha256:...",
  "timestamp_utc": "2026-06-14T09:23:17.123Z",
  "edge_or_cloud": "edge",
  "signature": "ed25519:...",
  "replay_url": "s3://sentinel-evidence/recv_.../replay.mp4"
}
```

Receipts are stored in S3 + DynamoDB, optionally with Amazon QLDB for tamper-evidence.

---

## 11. Pricing and Business Model

### Pricing tiers
| Tier | Who | What's included | Price |
|---|---|---|---|
| **Sentinel Core** | Researchers, students, hobbyists | Open-source SDK, 2 invariant templates, community support | Free |
| **Sentinel Pilot** | Design partners | 1 robot, full verifier, dashboard, 30-day trial, case-study requirement | Free |
| **Sentinel Growth** | Startups, mid-size fleets | Up to 25 robots, all templates, ROS2/Isaac ROS integration, email support | $2,500/robot/month (annual) or $3,000 month-to-month |
| **Sentinel Enterprise** | OEMs, defense, medical | Unlimited robots, custom invariants, edge TEE/hardening, audit reports, SLA, dedicated support | $150K–$500K/year + $50K–$200K implementation |

### Unit economics
| Metric | Growth | Enterprise |
|---|---|---|
| Avg robots/customer | 10 | 100+ |
| ARR/customer | $300K | $250K–$500K |
| Gross margin | ~80% | ~85% |
| Sales cycle | 1–3 months | 6–18 months |

### Revenue milestones
- First paid Growth deal: $30K–$75K ARR.
- First Enterprise deal: $150K–$300K ARR.
- Strategic acquisition range with 2–3 design partners + production pilot: mid-seven figures USD.

---

## 12. Competitive Landscape

| Competitor | What they do | Sentinel differentiation |
|---|---|---|
| NVIDIA Halos | Full-stack cloud-to-robot safety | Model-agnostic; works outside NVIDIA stack; lighter edge footprint |
| 3Laws | Robot safety middleware, ROS plugin | Predictive physics-aware verification + audit receipts |
| Dexterity Foresight | World model for manipulation | Independent layer, not tied to Dexterity robots |
| Edge Case Research nLoop | Safety intelligence platform | Live runtime product vs. safety-case consulting |
| AgentGuard / WedgeSecure / Cordum | Runtime governance for software agents | Extends to physical actuators at the edge |
| Academic CBF/Simplex | Research-grade safety filters | Productized, packaged, integrated with Isaac Sim/ROS2 |

**White space:** No independent, model-agnostic, physics-aware runtime verifier for physical AI exists as a commercial product.

---

## 13. Go-to-Market

### Phase 0: Beachhead (Weeks 1–8)
- Build Isaac Sim demo of Sentinel catching unsafe AMR/humanoid trajectories.
- Target warehouse AMR + humanoid fleet coexistence.

### Phase 1: Design Partners (Weeks 8–20)
- Land 3 design partners from logistics robotics.
- Free pilots in exchange for data, case studies, and co-development feedback.
- Warmest leads: NVIDIA Inception, MassRobotics, AWS Physical AI Fellowship network.

### Phase 2: Productize & Land Pilots (Months 6–12)
- SDK + dashboard + edge runtime.
- Per-robot-per-month pricing.
- ROS2 + Isaac ROS + Jetson integrations.
- Publish benchmark: "Sentinel prevented X unsafe actions in Y hours."

### Phase 3: Strategic Options (Months 12–24)
- Acquisition conversations with OEMs, autonomy stacks, and AI safety platforms.
- Strategic partnerships with NVIDIA, AWS, MassRobotics.
- Enterprise licenses for construction, agriculture, and medical buyers.

### Marketing tactics
1. Build "Verified Physical AI" category narrative.
2. Lead with 90-second demo video.
3. Publish three technical essays:
   - "The Cryptographic Wall in Physical AI"
   - "Why Simulation Can't Authorize Robot Actions"
   - "From CBF Research to Production Runtime Safety"
4. Target NVIDIA ecosystem: GTC, Inception, Isaac ROS integration.
5. Participate in ISO/TC 299 and ISO/IEC JTC 1/SC 42.
6. Offer free 2-week "safety audit" Trojan horse pilot.

---

## 14. Strategic Acquisition Targets

| Buyer Type | Why they'd buy | Examples |
|---|---|---|
| Robot brain / physical AI startups | Need safety feature; faster to acquire than build | Skild AI, Physical Intelligence, Field AI, Covariant, Dexterity |
| Industrial robot OEMs | Software differentiation; safety moat | ABB, KUKA, FANUC, Universal Robots, SoftBank |
| Autonomy / defense primes | Runtime assurance for high-stakes autonomy | Anduril, Shield AI, Saronic, Skydio, Mobileye |
| Construction / ag OEMs | Buying autonomy stacks; safety missing | Caterpillar, John Deere, Komatsu, Volvo |
| Medical robotics | Verifiable actuation records for FDA/auditors | CMR Surgical, Medtronic, J&J MedTech, Intuitive |
| AI safety / agent governance | Extend software-agent governance to physical | AgentGuard, WedgeSecure, Cordum, OpenAI, Anthropic |

---

## 15. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| NVIDIA builds it into Halos | Stay model-agnostic and edge-light; serve non-NVIDIA stacks |
| Long sales cycles in heavy industry | Start with logistics (fastest deployment) |
| Liability if Sentinel misses something | Position as defense-in-depth, not sole safety system; clear EULA |
| Hard to prove value without real robots | Partner with sim-to-real programs and MassRobotics/AWS/NVIDIA fellows |
| Regulatory uncertainty | Track/contribute to ISO/TC 299; map features to standards |

---

## 16. MVP Scope (4 Weeks)

### Goal
A working simulation-first demo that can be shown to design partners and posted publicly:
- Parameterized warehouse scene in Isaac Sim
- AMR/humanoid planner proposing trajectories
- Sentinel verifier catching unsafe actions (collision, speed, geofence)
- Dashboard showing verdict stream and replay
- Public GitHub repo with open-source Core SDK

### Week 1: Foundation
- Set up AWS account, IAM, billing alerts.
- Create GitHub repo `sentinel-ai/sentinel-core`.
- Containerize Isaac Sim 4.2 on EC2 g5/g6.
- Build Scene Forge v0.1: generate warehouse scenario (floor, aisles, pallets, human obstacles).
- Define action schema and receipt schema.

### Week 2: Verifier Core
- Build Sentinel Verifier v0.1 with three invariants:
  - Collision-free
  - Speed envelope
  - Geofence
- Integrate with Isaac Sim physics step.
- Build Planner Adapter v0.1: simple heuristic planner + customer planner stub.
- Produce first end-to-end verdict.

### Week 3: Dashboard & Evidence
- Build Command Center skeleton (Next.js + FastAPI backend).
- Show real-time verdict stream.
- Add incident replay with Isaac Sim scene.
- Build Evidence Vault v0.1: store signed receipts in S3 + DynamoDB.
- Generate first safety case report.

### Week 4: Polish & GTM
- Record 90-second demo video.
- Write README, architecture doc, and first technical essay.
- Open-source `sentinel-core` SDK.
- Identify 20 design partner prospects.
- Draft personalized outreach sequence.
- Apply to NVIDIA Inception.

### MVP success criteria
| Criterion | Target |
|---|---|
| Demo catches unsafe trajectory | ≥3 invariant violations demonstrated |
| Verifier latency (cloud) | <500 ms |
| Dashboard shows live verdict stream | Yes |
| Public repo with docs | Yes |
| 20 design partner targets identified | Yes |
| 5 outreach emails sent | Yes |
| NVIDIA Inception application submitted | Yes |

### Out of MVP scope
- Verifier Nano edge runtime
- Policy Forge UI (basic YAML editing only)
- Custom invariant authoring
- Multi-robot fleet coordination
- TEE/hardened edge deployment
- Medical or defense certification mapping

---

## 17. Decisions Log

- **13 Jun 2026:** Moved away from fintech; selected trust/verification for autonomous AI as direction.
- **14 Jun 2026:** Chose Sentinel over Receipts and Consensus.
- **14 Jun 2026:** Confirmed software-only + AWS-native approach.
- **14 Jun 2026:** Selected NVIDIA Isaac Sim for simulation engine.
- **14 Jun 2026:** Adjusted beachhead to warehouse AMR + humanoid fleet safety.
- **14 Jun 2026:** Approved three-layer architecture, components, interfaces, data flow, pricing, and 4-week MVP scope.

---

## 18. Open Questions

1. Do we commit to a public GitHub org name now (`sentinel-ai`, `verified-physical-ai`, or other)?
2. Should the first demo use a prebuilt Isaac Sim warehouse asset or build a custom scene?
3. Do we prioritize ROS2 integration in MVP, or keep the Planner Adapter generic REST/JSON first?
4. What is the AWS account budget ceiling for the first month of compute?
5. Do we want to file a provisional patent on the verifier architecture before public release?

---

## 19. Next Steps

1. User reviews and approves this written spec.
2. Invoke `writing-plans` skill to create detailed implementation plan.
3. Begin Week 1 MVP execution.

---

*Spec author: Claude for Satyam Das · Last updated: 2026-06-14*
