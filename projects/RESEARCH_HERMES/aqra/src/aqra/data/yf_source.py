import logging

import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


class YFSource:
    def fetch_ohlcv_many(self, tickers: list[str], start: str, end: str,
                         batch_size: int = 50) -> pd.DataFrame:
        """Batched multi-ticker download -> long-format frame matching raw_prices."""
        frames = []
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            try:
                data = yf.download(batch, start=start, end=end, progress=False,
                                   auto_adjust=False, group_by="ticker", threads=True)
            except Exception as e:
                logger.warning("Batch %d-%d download failed: %s", i, i + len(batch), e)
                continue
            if data is None or data.empty:
                continue
            for t in batch:
                try:
                    sub = data[t] if isinstance(data.columns, pd.MultiIndex) else data
                except KeyError:
                    continue
                sub = sub.dropna(how="all")
                if sub.empty:
                    continue
                sub = sub.reset_index()
                sub.columns = [str(c).lower().replace(" ", "_") for c in sub.columns]
                if "adj_close" not in sub.columns:
                    sub["adj_close"] = sub.get("close")
                out = pd.DataFrame({
                    "ticker": t,
                    "date": pd.to_datetime(sub["date"]).dt.normalize(),
                    "open": sub["open"],
                    "high": sub["high"],
                    "low": sub["low"],
                    "close": sub["close"],
                    "volume": sub["volume"].fillna(0),
                    "adjusted_close": sub["adj_close"],
                    "source": "yfinance",
                }).dropna(subset=["close"])
                frames.append(out)
            logger.info("Downloaded batch %d-%d (%d tickers so far ok)",
                        i, i + len(batch), len(frames))
        if not frames:
            return pd.DataFrame(columns=["ticker", "date", "open", "high", "low",
                                         "close", "volume", "adjusted_close", "source"])
        return pd.concat(frames, ignore_index=True)

    def fetch_ohlcv(self, ticker: str, start: str, end: str) -> pd.DataFrame:
        data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
        if data.empty:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "adjusted_close"])
        data = data.reset_index()
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [c[0].lower() for c in data.columns]
        else:
            data.columns = [str(c).lower() for c in data.columns]
        rename = {
            "date": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
            "adj close": "adjusted_close",
            "adj_close": "adjusted_close",
        }
        data = data.rename(columns={k: v for k, v in rename.items() if k in data.columns})
        data["date"] = pd.to_datetime(data["date"]).dt.normalize()
        data["ticker"] = ticker
        data["source"] = "yfinance"
        return data[["ticker", "date", "open", "high", "low", "close", "volume", "adjusted_close", "source"]]
