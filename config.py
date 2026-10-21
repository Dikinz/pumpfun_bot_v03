import os
from types import SimpleNamespace
from dotenv import load_dotenv
load_dotenv()
def f(k,d): return float(os.getenv(k,d))
def i(k,d): return int(os.getenv(k,d))
settings=SimpleNamespace(
 api_key=os.getenv("PUMPPORTAL_API_KEY","").strip(),
 database_path=os.getenv("DATABASE_PATH","data/trades.db"),
 start_balance=f("START_BALANCE",30), position_size=f("POSITION_SIZE",3),
 max_positions=i("MAX_POSITIONS",2), min_score=i("MIN_SCORE",80),
 stop_loss_pct=f("STOP_LOSS_PCT",-0.10), tp1_pct=f("TP1_PCT",0.18),
 tp2_pct=f("TP2_PCT",0.35), trailing_stop_pct=f("TRAILING_STOP_PCT",0.08),
 daily_max_loss_pct=f("DAILY_MAX_LOSS_PCT",0.15), emergency_balance=f("EMERGENCY_BALANCE",20),
 observation_seconds=i("OBSERVATION_SECONDS",15), min_trades_for_entry=i("MIN_TRADES_FOR_ENTRY",12),
 min_buy_sell_ratio=f("MIN_BUY_SELL_RATIO",1.50), min_unique_buyers=i("MIN_UNIQUE_BUYERS",7),
 min_market_cap_sol=f("MIN_MARKET_CAP_SOL",18), max_market_cap_sol=f("MAX_MARKET_CAP_SOL",180),
 max_watched_tokens=i("MAX_WATCHED_TOKENS",5), watch_seconds=i("WATCH_SECONDS",20),
 snapshot_seconds=i("SNAPSHOT_SECONDS",10), max_price_jump_ratio=f("MAX_PRICE_JUMP_RATIO",20),
 min_price_samples=i("MIN_PRICE_SAMPLES",5), min_short_momentum_pct=f("MIN_SHORT_MOMENTUM_PCT",0.015),
 max_short_momentum_pct=f("MAX_SHORT_MOMENTUM_PCT",0.45), max_signal_age_seconds=i("MAX_SIGNAL_AGE_SECONDS",90),
 cooldown_seconds=i("COOLDOWN_SECONDS",120), dead_token_seconds=i("DEAD_TOKEN_SECONDS",8),
 watchlist_rebalance_seconds=i("WATCHLIST_REBALANCE_SECONDS",10), watchlist_min_age_seconds=i("WATCHLIST_MIN_AGE_SECONDS",5),
 watchlist_evict_margin=f("WATCHLIST_EVICT_MARGIN",8),
 # Cost Optimizer v0.4.4.4
 free_min_market_cap_sol=f("FREE_MIN_MARKET_CAP_SOL",20),
 free_max_market_cap_sol=f("FREE_MAX_MARKET_CAP_SOL",120),
 free_min_initial_buy_sol=f("FREE_MIN_INITIAL_BUY_SOL",0.0),
 max_paid_trade_events=i("MAX_PAID_TRADE_EVENTS",50000),
 max_paid_subscriptions=i("MAX_PAID_SUBSCRIPTIONS",250),
 paid_event_cost_sol_per_10k=f("PAID_EVENT_COST_SOL_PER_10K",0.01),
 cost_guard_enabled=i("COST_GUARD_ENABLED",1),
)
