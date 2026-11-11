"""
Meme coin discovery scanner.

Uses CoinGecko's public API to rank meme-token market activity.
This is a discovery/risk-screening tool, NOT a price prediction system.
Public API rate limits and category availability may vary.
"""

import requests
import pandas as pd

BASE_URL = "https://api.coingecko.com/api/v3"
CATEGORY = "meme-token"


def fetch_meme_coins(per_page=100):
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "category": CATEGORY,
        "order": "volume_desc",
        "per_page": min(max(int(per_page), 1), 250),
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d,30d",
    }
    response = requests.get(
        url,
        params=params,
        timeout=20,
        headers={"accept": "application/json"},
    )
    if response.status_code == 429:
        raise RuntimeError("CoinGecko rate limit reached. Wait and try again later.")
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list):
        raise RuntimeError("Unexpected response from market data provider.")
    return payload


def rank_meme_coins(
    per_page=100,
    min_market_cap_usd=2_000_000,
    min_volume_usd=500_000,
    min_volume_to_cap=0.03,
):
    """
    Return a watchlist sorted by a transparent activity score.

    Filters are deliberately configurable and do not guarantee liquidity,
    safety, exchange availability, or future returns.
    """
    coins = fetch_meme_coins(per_page=per_page)
    rows = []

    for coin in coins:
        market_cap = coin.get("market_cap") or 0
        volume = coin.get("total_volume") or 0
        price = coin.get("current_price")
        change_24h = coin.get("price_change_percentage_24h")
        change_7d = coin.get("price_change_percentage_7d_in_currency")
        change_30d = coin.get("price_change_percentage_30d_in_currency")
        high_24h = coin.get("high_24h")
        low_24h = coin.get("low_24h")

        if not price or not market_cap or not volume:
            continue
        if market_cap < min_market_cap_usd or volume < min_volume_usd:
            continue

        volume_to_cap = volume / market_cap if market_cap else 0
        if volume_to_cap < min_volume_to_cap:
            continue

        # A transparent heuristic score, not a learned probability.
        # Clip extreme returns so one manipulated print cannot dominate.
        c24 = max(-30, min(30, float(change_24h or 0)))
        c7 = max(-50, min(50, float(change_7d or 0)))
        c30 = max(-75, min(75, float(change_30d or 0)))

        momentum_score = (
            0.45 * c24 +
            0.40 * c7 +
            0.15 * c30
        )

        # Reward meaningful turnover, but cap its contribution.
        turnover_score = min(volume_to_cap * 100, 20)

        # Penalise exceptionally large 24h ranges as a simple risk warning.
        range_pct = None
        if high_24h and low_24h and price:
            range_pct = ((high_24h - low_24h) / price) * 100
        volatility_penalty = min((range_pct or 0) * 0.15, 10)

        activity_score = momentum_score + turnover_score - volatility_penalty

        warnings = []
        if volume_to_cap > 2:
            warnings.append("Extreme turnover: verify wash trading / data quality")
        if range_pct is not None and range_pct > 40:
            warnings.append("Very wide 24h range")
        if market_cap < 10_000_000:
            warnings.append("Small market cap: high manipulation / liquidity risk")
        if (change_24h or 0) > 50:
            warnings.append("Already surged over 50% in 24h; chasing risk")
        if (change_24h or 0) < -25:
            warnings.append("Sharp 24h decline")

        rows.append({
            "name": coin.get("name"),
            "symbol": (coin.get("symbol") or "").upper(),
            "coin_id": coin.get("id"),
            "price_usd": price,
            "market_cap_usd": market_cap,
            "volume_24h_usd": volume,
            "volume_market_cap_ratio": volume_to_cap,
            "change_24h_pct": change_24h,
            "change_7d_pct": change_7d,
            "change_30d_pct": change_30d,
            "range_24h_pct": range_pct,
            "activity_score": activity_score,
            "risk_flags": "; ".join(warnings) if warnings else "No basic filter warning",
            "coingecko_url": f"https://www.coingecko.com/en/coins/{coin.get('id')}",
        })

    if not rows:
        return pd.DataFrame()

    result = pd.DataFrame(rows)
    return result.sort_values("activity_score", ascending=False).reset_index(drop=True)
