import yfinance as yf
import pandas as pd

class YFSource:
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
