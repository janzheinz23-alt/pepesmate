import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline

from indicators import calculate_indicators
from market_data import get_market_data

FEATURES = [
    "return_1", "return_3", "return_7", "rsi",
    "ema_gap", "macd", "macd_signal", "bb_position",
    "volume_ratio", "atr_percent", "volatility",
]

MIN_CONFIDENCE = 0.58
MAX_CONFIDENCE = 0.42


def analyse_asset(name: str, ticker: str) -> dict:
    raw = get_market_data(ticker)
    df = calculate_indicators(raw)

    future_close = df["Close"].shift(-1)
    df["target"] = (future_close > df["Close"]).where(future_close.notna()).astype(float)
    df = df.replace([np.inf, -np.inf], np.nan)

    features = df[FEATURES].dropna()
    known = df.loc[features.index, "target"].notna()
    X = features.loc[known]
    y = df.loc[X.index, "target"].astype(int)

    if len(X) < 250:
        raise ValueError(f"Only {len(X)} labelled rows available; need at least 250.")
    split = int(len(X) * 0.80)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    if y_train.nunique() < 2:
        raise ValueError("Training sample has only one class.")

    model = make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(
            n_estimators=300, max_depth=5, min_samples_leaf=8,
            class_weight="balanced", random_state=42, n_jobs=-1
        ),
    )
    model.fit(X_train, y_train)
    accuracy = accuracy_score(y_test, model.predict(X_test))
    baseline = max(y_train.mean(), 1 - y_train.mean())

    # Refit using all completed historical labels for the latest estimate.
    model.fit(X, y)
    latest_features = features.iloc[[-1]]
    probs = model.predict_proba(latest_features)[0]
    classes = list(model.classes_)
    if 1 not in classes:
        raise ValueError("Model did not learn the upward class.")
    up_probability = float(probs[classes.index(1)])

    row = df.loc[latest_features.index[-1]]
    price = float(row["Close"])
    atr = float(row["atr"])
    rsi = float(row["rsi"])
    bullish = float(row["ema9"]) > float(row["ema21"]) and price > float(row["ema50"])
    bearish = float(row["ema9"]) < float(row["ema21"]) and price < float(row["ema50"])
    momentum = float(row["macd"]) > float(row["macd_signal"])
    beats_baseline = accuracy > baseline

    signal = "NO TRADE"
    if (
        up_probability >= MIN_CONFIDENCE and bullish and momentum
        and 35 < rsi < 70 and beats_baseline
    ):
        signal = "POTENTIAL BUY - REVIEW MANUALLY"
    elif up_probability <= MAX_CONFIDENCE and bearish and beats_baseline:
        signal = "BEARISH - AVOID BUYING"

    return {
        "asset": name,
        "price": price,
        "up_probability": up_probability,
        "rsi": rsi,
        "accuracy": float(accuracy),
        "baseline": float(baseline),
        "volume_ratio": float(row["volume_ratio"]),
        "signal": signal,
        "stop_loss": price - 1.5 * atr,
        "take_profit": price + 2.25 * atr,
        "details": {
            "bullish_trend": bool(bullish),
            "bearish_trend": bool(bearish),
            "positive_macd_momentum": bool(momentum),
            "model_beats_majority_baseline": bool(beats_baseline),
            "labelled_training_rows": int(len(X)),
            "holdout_rows": int(len(y_test)),
        },
    }
