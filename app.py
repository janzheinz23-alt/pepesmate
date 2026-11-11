import streamlit as st
import pandas as pd
from meme_scanner import rank_meme_coins
from trading_engine import analyse_asset
from market_data import ASSETS

st.set_page_config(page_title="XRP + PEPE AI Terminal", page_icon="📈", layout="wide")

st.title("📈 XRP + PEPE AI Trading Terminal")
st.caption("Research dashboard • Manual approval only • No exchange connection")

st.warning(
    "Experimental analysis only. Signals are not guarantees or financial advice. "
    "No trades are placed by this app. Verify prices and fees in your exchange before acting."
)

with st.sidebar:
    st.header("Scanner settings")
    selected = st.multiselect("Assets", list(ASSETS.keys()), default=list(ASSETS.keys()))
    st.info("Current version analyses daily candles. It is not a 5-minute scalping system.")
    run_scan = st.button("Run market scan", type="primary", use_container_width=True)

if "scan_results" not in st.session_state:
    st.session_state.scan_results = []

if run_scan:
    results = []
    progress = st.progress(0)
    status = st.empty()
    for i, name in enumerate(selected):
        status.write(f"Analysing {name}…")
        try:
            results.append(analyse_asset(name, ASSETS[name]))
        except Exception as exc:
            results.append({"asset": name, "error": str(exc)})
        progress.progress((i + 1) / max(len(selected), 1))
    st.session_state.scan_results = results
    status.success("Scan complete.")

if not selected:
    st.info("Choose at least one asset in the sidebar.")
elif not st.session_state.scan_results:
    st.info("Select assets and press **Run market scan** to generate analysis.")

for result in st.session_state.scan_results:
    if "error" in result:
        st.error(f"{result['asset']}: {result['error']}")
        continue

    st.subheader(result["asset"])
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest close (USD)", f"{result['price']:.8g}")
    c2.metric("Estimated next-day rise", f"{result['up_probability']:.1%}")
    c3.metric("RSI", f"{result['rsi']:.1f}")
    c4.metric("Holdout accuracy", f"{result['accuracy']:.1%}")

    st.write(f"**Signal:** {result['signal']}")
    st.caption(
        f"Majority baseline: {result['baseline']:.1%} · "
        f"Volume / 20-day average: {result['volume_ratio']:.2f} · "
        f"Forecast horizon: next daily candle"
    )

    if result["signal"] == "POTENTIAL BUY - REVIEW MANUALLY":
        risk_cols = st.columns(3)
        risk_cols[0].metric("Reference entry", f"${result['price']:.8g}")
        risk_cols[1].metric("ATR stop reference", f"${result['stop_loss']:.8g}")
        risk_cols[2].metric("ATR target reference", f"${result['take_profit']:.8g}")
        st.warning("Review the chart, liquidity, spread and fees. No order has been placed.")

    with st.expander(f"{result['asset']} technical details"):
        st.json(result["details"])

st.divider()
st.subheader("Trade journal")
st.caption("This simple journal is session-only; entries disappear when the app session resets.")
with st.form("journal_form"):
    asset = st.selectbox("Asset", list(ASSETS.keys()))
    action = st.selectbox("Decision", ["Watch", "Paper buy", "Paper sell", "No trade"])
    notes = st.text_input("Notes")
    submitted = st.form_submit_button("Add journal entry")
    if submitted:
        if "journal" not in st.session_state:
            st.session_state.journal = []
        st.session_state.journal.append(
            {"Asset": asset, "Decision": action, "Notes": notes}
        )

if st.session_state.get("journal"):
    st.dataframe(pd.DataFrame(st.session_state.journal), use_container_width=True)

st.caption("Data provider: Yahoo Finance via yfinance. Data availability and timing may vary.")


st.divider()
st.header("🚀 Meme coin discovery")
st.caption(
    "Ranks meme-token market activity using public CoinGecko market data. "
    "Scores are heuristics, not probabilities or buy recommendations."
)

with st.expander("Discovery filters", expanded=True):
    scan_count = st.selectbox("Coins to request", [50, 100, 200], index=1)
    min_cap = st.number_input(
        "Minimum market cap (USD)", min_value=100_000,
        max_value=1_000_000_000, value=2_000_000, step=500_000
    )
    min_volume = st.number_input(
        "Minimum 24h volume (USD)", min_value=10_000,
        max_value=100_000_000, value=500_000, step=100_000
    )
    min_turnover = st.slider(
        "Minimum 24h volume / market cap", 0.0, 1.0, 0.03, 0.01
    )
    discover = st.button("Discover meme coin opportunities", type="primary")

if discover:
    try:
        with st.spinner("Fetching and ranking meme-token market activity…"):
            meme_results = rank_meme_coins(
                per_page=scan_count,
                min_market_cap_usd=min_cap,
                min_volume_usd=min_volume,
                min_volume_to_cap=min_turnover,
            )
        st.session_state.meme_results = meme_results
    except Exception as exc:
        st.error(
            f"Meme scanner could not retrieve data: {exc}. "
            "Check your connection or wait if the public API is rate-limited."
        )

if "meme_results" in st.session_state:
    meme_results = st.session_state.meme_results
    if meme_results.empty:
        st.info("No coins passed these filters. Try relaxing them carefully.")
    else:
        display_columns = [
            "name", "symbol", "price_usd", "market_cap_usd",
            "volume_24h_usd", "change_24h_pct", "change_7d_pct",
            "activity_score", "risk_flags",
        ]
        st.dataframe(
            meme_results[display_columns],
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download scanner results (CSV)",
            data=meme_results.to_csv(index=False).encode("utf-8"),
            file_name="meme_coin_watchlist.csv",
            mime="text/csv",
        )
        st.caption(
            "A high activity score can reflect a coin that has already surged. "
            "Check contract authenticity, exchange availability, liquidity, "
            "holder concentration, unlocks, spread and slippage independently. "
            "This scanner does not detect scams or guarantee that a token can be sold."
        )
