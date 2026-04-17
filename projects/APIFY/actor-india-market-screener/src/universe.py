"""
Hardcoded stock universes. NOT user-controlled.
Ported from NeuralQuant universe.py — NSE tickers use .NS suffix for yfinance.
"""

US_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B",
    "JPM", "V", "MA", "UNH", "XOM", "JNJ", "PG", "HD", "COST", "ABBV",
    "MRK", "LLY", "CVX", "BAC", "NFLX", "ORCL", "ADBE", "CRM", "AMD",
    "INTC", "QCOM", "TXN", "AVGO", "WMT", "TGT", "NKE", "MCD", "SBUX",
    "DIS", "PFE", "AMGN", "GILD", "ISRG",
]

# NSE tickers with .NS suffix for yfinance
IN_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
    "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "LT.NS",
    "HCLTECH.NS", "WIPRO.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "ULTRACEMCO.NS", "BAJFINANCE.NS", "TITAN.NS", "NESTLEIND.NS", "POWERGRID.NS",
    "NTPC.NS", "ONGC.NS", "COALINDIA.NS", "TATASTEEL.NS", "JSWSTEEL.NS",
    "HINDALCO.NS", "ADANIPORTS.NS", "DMART.NS", "PIDILITIND.NS", "EICHERMOT.NS",
    "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS",
    "APOLLOHOSP.NS", "ZOMATO.NS", "IRCTC.NS", "MUTHOOTFIN.NS", "BANDHANBNK.NS",
]


def get_universe(market: str) -> list[str]:
    if market == "India":
        return IN_UNIVERSE
    if market == "US":
        return US_UNIVERSE
    return IN_UNIVERSE + US_UNIVERSE  # both