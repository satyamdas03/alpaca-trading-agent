# Sentinel

> Runtime safety verifier for physical AI.

Sentinel is an AWS-native safety envelope between AI planners and physical actuators. It verifies every proposed robot action in simulation before execution, then continues verifying live actions at the edge.

## Quick Start

```bash
# Install Python package
pip install -e ".[dev]"

# Run tests
pytest

# Run cloud demo
python scripts/run_cloud_demo.py
```

## Repository Layout

```
sentinel/
├── cdk/                 # AWS CDK infrastructure
├── packages/
│   ├── scene_forge/     # Scenario generation (Isaac Sim)
│   ├── sentinel_verifier/   # Cloud verifier service
│   ├── verifier_nano/   # Lightweight edge verifier
│   ├── edge_telemetry/  # Mock robot + MQTT bridge
│   ├── policy_forge/    # Policy authoring UI/CLI
│   └── command_center/  # Web dashboard
├── scenarios/           # Test scenarios
├── policies/            # Example policies
└── scripts/             # Demo + utility scripts
```

## License

Proprietary — Satyam Das, 2026.
