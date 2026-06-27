from pathlib import Path
from datetime import datetime, timezone


class TradeLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, order: dict):
        ts = datetime.now(timezone.utc).isoformat()
        line = f"{ts} | {order.get('side')} {order.get('qty')} {order.get('ticker')} @ {order.get('price')} | strategy={order.get('strategy_id')}\n"
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)
