XRP + PEPE AI TRADING TERMINAL
==============================

FREE-TIER DEPLOYMENT PACKAGE
This is a Streamlit dashboard project intended for Streamlit Community Cloud.
GitHub is used to store the source code. Free-tier limits and service terms apply.

PROJECT FILES
- app.py: Streamlit dashboard
- trading_engine.py: model training and signal filters
- indicators.py: RSI, EMA, MACD, Bollinger Bands, volume and ATR
- market_data.py: Yahoo Finance data retrieval
- risk_manager.py: illustrative position sizing helper
- backtesting.py: chronological directional holdout evaluation
- trade_journal.py: CSV journal helper
- requirements.txt: Python dependencies
- .streamlit/config.toml: dashboard theme

DEPLOY
1. Extract this ZIP.
2. Create a PRIVATE GitHub repository.
3. Upload all files, including the .streamlit folder.
4. Visit https://share.streamlit.io/ and sign in with GitHub.
5. Choose the repository, branch (usually main), and main file path app.py.
6. Deploy.

IMPORTANT LIMITATIONS
- This starter app uses daily candles and forecasts the next daily candle.
- It is not a 5-minute or 15-minute scalping bot.
- Yahoo Finance availability, ticker coverage, and data timing can vary.
- PEPE data may be unavailable or inconsistent for some periods.
- Model confidence and directional accuracy do not prove profitability.
- The holdout accuracy is not a complete trading backtest.
- Fees, spread, slippage, liquidity, exchange price differences and NZD/USD conversion
  are not included in the displayed ATR reference levels.
- Journal entries in the dashboard are session-only. Use trade_journal.py for a
  local CSV journal if you adapt the app to call it.
- No Revolut connection, API keys, wallet connection, or order execution exists.
- Manual approval only. No leverage. Do not enter API secrets into GitHub.

TEST FIRST
Use paper trading and independently verify data, calculations, fees and historical
performance before considering real-money decisions. This is experimental software,
not financial advice or a promise of returns.


MEME COIN DISCOVERY ADD-ON
- meme_scanner.py queries CoinGecko's public meme-token category.
- The Streamlit app has a discovery panel with configurable market-cap,
  volume and turnover filters.
- Results are ranked using a transparent activity heuristic based on
  24h/7d/30d momentum, turnover and a simple volatility penalty.
- This is NOT a prediction that a coin will skyrocket and NOT a buy signal.
- Public API rate limits, missing data, category coverage and token listings vary.
- The scanner does not verify smart-contract safety, holder concentration,
  exchange listing, ability to sell, or actual order-book depth.
- Verify each token independently before considering any trade.
