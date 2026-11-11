"""Basic chronological directional model evaluation; not a profitability backtest."""

from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.pipeline import make_pipeline

from indicators import calculate_indicators
from market_data import get_market_data

FEATURES = [
    "return_1", "return_3", "return_7", "rsi",
    "ema_gap", "macd", "macd_signal", "bb_position",
    "volume_ratio", "atr_percent", "volatility",
]


def evaluate(ticker: str) -> dict:
    df = calculate_indicators(get_market_data(ticker))
    future = df["Close"].shift(-1)
    df["target"] = (future > df["Close"]).where(future.notna()).astype(float)
    df = df.replace([float("inf"), float("-inf")], float("nan"))
    X = df[FEATURES].dropna()
    valid = df.loc[X.index, "target"].notna()
    X = X.loc[valid]
    y = df.loc[X.index, "target"].astype(int)
    split = int(len(X) * 0.8)
    if split < 100 or len(X) - split < 20:
        raise ValueError("Not enough rows for a meaningful holdout evaluation.")
    model = make_pipeline(
        SimpleImputer(strategy="median"),
        RandomForestClassifier(
            n_estimators=300, max_depth=5, min_samples_leaf=8,
            class_weight="balanced", random_state=42, n_jobs=-1
        ),
    )
    model.fit(X.iloc[:split], y.iloc[:split])
    pred = model.predict(X.iloc[split:])
    return {
        "accuracy": accuracy_score(y.iloc[split:], pred),
        "baseline": max(y.iloc[:split].mean(), 1 - y.iloc[:split].mean()),
        "confusion_matrix": confusion_matrix(y.iloc[split:], pred, labels=[0, 1]).tolist(),
        "warning": "Directional accuracy is not trading profitability. This does not model fees, slippage, fills or position sizing.",
    }
