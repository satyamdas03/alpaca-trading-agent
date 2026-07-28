"""Strategy DSL parser and backtest orchestrator (MVP pure-Python)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path

import yaml


@dataclass
class Strategy:
    """Parsed Aureum Quant Kernel strategy."""

    api_version: str
    kind: str
    metadata: Dict[str, Any]
    spec: Dict[str, Any]

    @classmethod
    def from_yaml(cls, text: str) -> "Strategy":
        data = yaml.safe_load(text)
        return cls(
            api_version=data.get("apiVersion", ""),
            kind=data.get("kind", ""),
            metadata=data.get("metadata", {}),
            spec=data.get("spec", {}),
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "Strategy":
        path = Path(path)
        return cls.from_yaml(path.read_text(encoding="utf-8"))

    def validate(self) -> List[str]:
        """Return a list of validation errors, empty if valid."""
        errors: List[str] = []
        if not self.metadata.get("name"):
            errors.append("metadata.name is required")
        spec = self.spec
        if "universe" not in spec:
            errors.append("spec.universe is required")
        if "schedule" not in spec:
            errors.append("spec.schedule is required")
        if "ranking" not in spec:
            errors.append("spec.ranking is required")
        if "weights" not in spec:
            errors.append("spec.weights is required")
        if "execution" not in spec:
            errors.append("spec.execution is required")
        return errors

    def constraints(self) -> List[Dict[str, Any]]:
        """Extract verifiable risk constraints."""
        risk = self.spec.get("risk", {})
        out = []
        for name in ["max_drawdown", "max_leverage", "max_turnover_annual"]:
            spec = risk.get(name)
            if spec:
                out.append(
                    {
                        "name": name,
                        "variable": name.replace("max_", ""),
                        "operator": "<=" if name.startswith("max_") else "==",
                        "limit": spec["value"],
                        "hard": spec.get("hard", False),
                    }
                )
        return out

    def to_dict(self) -> Dict[str, Any]:
        return {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": self.metadata,
            "spec": self.spec,
        }
