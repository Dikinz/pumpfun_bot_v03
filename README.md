# Pump.fun Bot v0.4.4.3 — Strategy Analyzer / PAPER ONLY

Based directly on the working v0.4.4.2 build. WebSocket parsing, Dynamic Watchlist,
Candidate Ranking, Entry Gates, risk limits, SL/TP/trailing rules are intentionally unchanged.

## Added in v0.4.4.3
For every PAPER entry the SQLite journal stores an entry snapshot:
score, age, trades, buy/sell ratio, unique buyers, momentum, market cap,
price sample count and watchlist rank.

For every exit it also stores:
PnL, MFE, MAE, holding time and exit reason.

`report.bat` now compares WINNERS vs LOSERS and prints an EXIT BREAKDOWN.
This build is for collecting a meaningful PAPER sample before changing strategy parameters.

## Run
1. Run `install_v0443.bat`.
2. Put `PUMPPORTAL_API_KEY=...` in `.env`.
3. Run `run_paper.bat`.
4. After a useful sample, stop the bot and run `report.bat`.

Do not put a wallet seed phrase/private key in this project. This build is PAPER ONLY.

## v0.4.4.4 Cost Optimizer
This build keeps PAPER execution and the v0.4.4.3 entry/exit strategy, but reduces paid token-trade streaming.

Cost controls:
- free launch gate before `subscribeTokenTrade`;
- only 5 simultaneous paid watches by default;
- 15 s observation / 20 s watch window;
- hard caps for paid trade events and paid subscriptions;
- automatic unsubscribe when the event cap is reached;
- `[COST]`/`[STREAM]`-style diagnostics include estimated SOL cost;
- tariff is configurable with `PAID_EVENT_COST_SOL_PER_10K` (estimator only).

Recommended first test: copy your API key into `.env`, keep all cost defaults unchanged, run `run_paper.bat` for 15-30 minutes, then stop it and run `report.bat`. Compare `paid_events`, `paid_subs`, exits and PnL with v0.4.4.3. Do not enable real-money execution; this package remains PAPER ONLY.
