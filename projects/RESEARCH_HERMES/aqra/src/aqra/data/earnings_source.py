import os
import logging

import pandas as pd

logger = logging.getLogger(__name__)


class EarningsSource:
    def fetch_calendar(
        self, ticker: str, start: str, end: str
    ) -> pd.DataFrame:
        api_key = os.getenv("EARNINGS_API_KEY")
        if not api_key:
            logger.warning("EARNINGS_API_KEY not set; returning empty earnings calendar")
            return pd.DataFrame(
                columns=[
                    "ticker",
                    "report_date",
                    "fiscal_quarter",
                    "eps_estimate",
                    "eps_actual",
                ]
            )

        try:
            import yfinance as yf

            cal = yf.Ticker(ticker).calendar
            if cal is None or (isinstance(cal, pd.DataFrame) and cal.empty):
                return pd.DataFrame(
                    columns=[
                        "ticker",
                        "report_date",
                        "fiscal_quarter",
                        "eps_estimate",
                        "eps_actual",
                    ]
                )
            if isinstance(cal, pd.DataFrame):
                cal = cal.copy()
                cal["ticker"] = ticker
                return cal
        except Exception as e:
            logger.warning("Failed to fetch earnings calendar for %s: %s", ticker, e)

        return pd.DataFrame(
            columns=[
                "ticker",
                "report_date",
                "fiscal_quarter",
                "eps_estimate",
                "eps_actual",
            ]
        )
