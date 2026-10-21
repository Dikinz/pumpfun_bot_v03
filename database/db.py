import sqlite3, json
from pathlib import Path
from datetime import datetime, timezone

def utcnow():
    return datetime.now(timezone.utc).isoformat()

class Database:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS tokens(
          mint TEXT PRIMARY KEY, symbol TEXT, name TEXT, creator TEXT, created_at TEXT,
          initial_buy REAL DEFAULT 0, market_cap_sol REAL DEFAULT 0, last_market_cap_sol REAL DEFAULT 0,
          trade_count INTEGER DEFAULT 0, buy_count INTEGER DEFAULT 0, sell_count INTEGER DEFAULT 0,
          unique_buyers INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS market_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, mint TEXT, event_type TEXT, signature TEXT,
          trader TEXT, sol_amount REAL, token_amount REAL, market_cap_sol REAL, raw_json TEXT
        );
        CREATE TABLE IF NOT EXISTS signals(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, mint TEXT, score INTEGER, decision TEXT, reason TEXT
        );
        CREATE TABLE IF NOT EXISTS paper_trades(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, mint TEXT, side TEXT, qty REAL, price REAL,
          notional_usd REAL, pnl_usd REAL, reason TEXT, score INTEGER, balance_after REAL
        );
        CREATE TABLE IF NOT EXISTS portfolio_snapshots(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, cash_usd REAL, equity_usd REAL, open_positions INTEGER
        );
        """)
        self.conn.commit()

    def upsert_token(self, mint, symbol="", name="", creator="", initial_buy=0, mc=0):
        self.conn.execute("""
        INSERT INTO tokens(mint,symbol,name,creator,created_at,initial_buy,market_cap_sol,last_market_cap_sol)
        VALUES(?,?,?,?,?,?,?,?)
        ON CONFLICT(mint) DO UPDATE SET
          symbol=excluded.symbol,name=excluded.name,creator=excluded.creator,
          initial_buy=excluded.initial_buy,last_market_cap_sol=excluded.last_market_cap_sol
        """,(mint,symbol,name,creator,utcnow(),float(initial_buy or 0),float(mc or 0),float(mc or 0)))
        self.conn.commit()

    def log_event(self, mint, event_type, raw=None, signature="", trader="", sol=0, tok=0, mc=0):
        self.conn.execute("""INSERT INTO market_events
        (ts,mint,event_type,signature,trader,sol_amount,token_amount,market_cap_sol,raw_json)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (utcnow(),mint,event_type,signature,trader,float(sol or 0),float(tok or 0),float(mc or 0),json.dumps(raw or {})))
        self.conn.commit()

    def update_trade_stats(self, mint, side, trader, mc):
        self.conn.execute("""UPDATE tokens SET trade_count=trade_count+1,
        buy_count=buy_count+?, sell_count=sell_count+?, last_market_cap_sol=? WHERE mint=?""",
        (1 if side=="buy" else 0, 1 if side=="sell" else 0, float(mc or 0), mint))
        if side == "buy" and trader:
            n = self.conn.execute("""SELECT COUNT(DISTINCT trader) FROM market_events
            WHERE mint=? AND event_type='trade' AND trader!='' AND json_extract(raw_json,'$.txType')='buy'""",(mint,)).fetchone()[0]
            self.conn.execute("UPDATE tokens SET unique_buyers=? WHERE mint=?",(n,mint))
        self.conn.commit()

    def get_token(self, mint):
        return self.conn.execute("SELECT * FROM tokens WHERE mint=?",(mint,)).fetchone()

    def log_signal(self, mint, score, decision, reason):
        self.conn.execute("INSERT INTO signals(ts,mint,score,decision,reason) VALUES(?,?,?,?,?)",
                          (utcnow(),mint,int(score),decision,reason))
        self.conn.commit()

    def log_trade(self, mint, side, qty, price, notional, pnl, reason, score, balance):
        self.conn.execute("""INSERT INTO paper_trades
        (ts,mint,side,qty,price,notional_usd,pnl_usd,reason,score,balance_after)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (utcnow(),mint,side,float(qty),float(price),float(notional),float(pnl),reason,int(score or 0),float(balance)))
        self.conn.commit()

    def snapshot(self, cash, equity, open_positions):
        self.conn.execute("INSERT INTO portfolio_snapshots(ts,cash_usd,equity_usd,open_positions) VALUES(?,?,?,?)",
                          (utcnow(),float(cash),float(equity),int(open_positions)))
        self.conn.commit()
