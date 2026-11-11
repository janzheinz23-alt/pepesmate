import pandas as pd


def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    close = df["Close"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    volume = df["Volume"].astype(float)

    df["return_1"] = close.pct_change()
    df["return_3"] = close.pct_change(3)
    df["return_7"] = close.pct_change(7)

    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    df["ema9"], df["ema21"], df["ema50"] = ema9, ema21, ema50
    df["ema_gap"] = (ema9 - ema21) / close

    delta = close.diff()
    gain, loss = delta.clip(lower=0), -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    rs = avg_gain / avg_loss.replace(0, float("nan"))
    df["rsi"] = 100 - (100 / (1 + rs))

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    df["macd"] = macd_line / close
    df["macd_signal"] = (macd_line - signal_line) / close

    middle = close.rolling(20).mean()
    std = close.rolling(20).std()
    upper, lower = middle + 2 * std, middle - 2 * std
    df["bb_position"] = (close - lower) / (upper - lower).replace(0, float("nan"))

    avg_volume = volume.rolling(20).mean().replace(0, float("nan"))
    df["volume_ratio"] = volume / avg_volume

    previous_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - previous_close).abs(), (low - previous_close).abs()],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(14).mean()
    df["atr"] = atr
    df["atr_percent"] = atr / close
    df["volatility"] = close.pct_change().rolling(14).std()
    return df
