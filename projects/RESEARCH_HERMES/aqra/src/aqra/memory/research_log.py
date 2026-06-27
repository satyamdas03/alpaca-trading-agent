from pathlib import Path
from datetime import datetime, timezone


class ResearchLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log_event(self, event_type: str, details: str):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"## {datetime.now(timezone.utc).isoformat()} — {event_type}\n{details}\n\n")
