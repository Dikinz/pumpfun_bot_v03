import sqlite3
from config import settings
c=sqlite3.connect(settings.database_path)
def one(q):
    r=c.execute(q).fetchone()
    return r[0] if r else 0
print("=== v0.3 Stats ===")
print("Tokens:",one("SELECT COUNT(*) FROM tokens"))
print("Events:",one("SELECT COUNT(*) FROM market_events"))
print("Signals:",one("SELECT COUNT(*) FROM signals"))
print("Paper trades:",one("SELECT COUNT(*) FROM paper_trades"))
print("Closed PnL USD:",round(one("SELECT COALESCE(SUM(pnl_usd),0) FROM paper_trades WHERE side='SELL'"),4))
