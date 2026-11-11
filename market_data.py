import yfinance as yf
import pandas as pd

ASSETS = {
    "XRP": "XRP-USD",
    "PEPE": "PEPE-USD",
}


def get_market_data(ticker: str) -> pd.DataFrame:
    data = yf.download(
        ticker, period="2y", interval="1d",
        auto_adjust=True, progress=False,
    )
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    if data.empty:
        raise ValueError(f"No data returned for {ticker}. Check ticker/data availability.")
    required = {"Close", "High", "Low", "Volume"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    return data
