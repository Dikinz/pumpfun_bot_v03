import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

def as_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1","true","yes","on"}

@dataclass(frozen=True)
class Settings:
    pumpportal_api_key: str = os.getenv("PUMPPORTAL_API_KEY","").strip()
    enable_metered_trade_stream: bool = as_bool("ENABLE_METERED_TRADE_STREAM", False)
    database_path: str = os.getenv("DATABASE_PATH","data/trades.db")
    start_balance: float = float(os.getenv("START_BALANCE","30"))
    position_size: float = float(os.getenv("POSITION_SIZE","5"))
    max_positions: int = int(os.getenv("MAX_POSITIONS","2"))
    min_score: int = int(os.getenv("MIN_SCORE","75"))
    stop_loss_pct: float = float(os.getenv("STOP_LOSS_PCT","-0.12"))
    tp1_pct: float = float(os.getenv("TP1_PCT","0.20"))
    tp2_pct: float = float(os.getenv("TP2_PCT","0.40"))
    trailing_stop_pct: float = float(os.getenv("TRAILING_STOP_PCT","0.10"))
    daily_max_loss_pct: float = float(os.getenv("DAILY_MAX_LOSS_PCT","0.15"))
    emergency_balance: float = float(os.getenv("EMERGENCY_BALANCE","20"))
    observation_seconds: int = int(os.getenv("OBSERVATION_SECONDS","30"))
    min_trades_for_entry: int = int(os.getenv("MIN_TRADES_FOR_ENTRY","8"))
    min_buy_sell_ratio: float = float(os.getenv("MIN_BUY_SELL_RATIO","1.35"))
    min_unique_buyers: int = int(os.getenv("MIN_UNIQUE_BUYERS","5"))
    max_market_cap_sol: float = float(os.getenv("MAX_MARKET_CAP_SOL","250"))
    min_market_cap_sol: float = float(os.getenv("MIN_MARKET_CAP_SOL","15"))
    max_creator_initial_buy: float = float(os.getenv("MAX_CREATOR_INITIAL_BUY","10"))
    demo_trade_feed: bool = as_bool("DEMO_TRADE_FEED", True)

settings = Settings()
