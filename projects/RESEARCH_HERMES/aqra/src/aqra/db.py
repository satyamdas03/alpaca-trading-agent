import duckdb
from pathlib import Path


class AQRADatabase:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(str(self.path))
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_prices (
                ticker TEXT,
                date DATE,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume BIGINT,
                adjusted_close DOUBLE,
                source TEXT,
                inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (ticker, date, source)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS lane_s_features (
                ticker TEXT,
                date DATE,
                mom_12_1 DOUBLE,
                pe_rank DOUBLE,
                pb_rank DOUBLE,
                quality_score DOUBLE,
                low_vol_score DOUBLE,
                insider_score DOUBLE,
                macro_regime TEXT,
                available_at DATE,
                PRIMARY KEY (ticker, date)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS lane_i_features (
                ticker TEXT,
                date DATE,
                overnight_gap DOUBLE,
                volume_zscore DOUBLE,
                news_sentiment_zscore DOUBLE,
                earnings_surprise DOUBLE,
                insider_event_score DOUBLE,
                available_at DATE,
                PRIMARY KEY (ticker, date)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS strategy_registry (
                id TEXT PRIMARY KEY,
                lane TEXT,
                name TEXT,
                signal_code TEXT,
                certified_at TIMESTAMP,
                status TEXT,
                meta JSON,
                live_weight DOUBLE DEFAULT 0.0
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                strategy_id TEXT,
                ticker TEXT,
                side TEXT,
                qty DOUBLE,
                price DOUBLE,
                filled_at TIMESTAMP,
                lane TEXT,
                pnl DOUBLE,
                FOREIGN KEY (strategy_id) REFERENCES strategy_registry(id)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_logs (
                id INTEGER PRIMARY KEY,
                event_type TEXT,
                event_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def list_tables(self) -> list[str]:
        rows = self.conn.execute("SHOW TABLES").fetchall()
        return [r[0] for r in rows]

    def close(self):
        self.conn.close()
