import json
from pathlib import Path


class PortfolioState:
    def __init__(self, path: Path):
        self.path = Path(path)

    def save(self, state: dict):
        self.path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    def load(self) -> dict:
        if not self.path.exists():
            return {"equity": 0.0, "positions": [], "allocations": []}
        return json.loads(self.path.read_text(encoding="utf-8"))
