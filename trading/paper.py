from dataclasses import dataclass

@dataclass
class Position:
    mint:str; qty:float; entry_price:float; notional:float; score:int; highest_price:float; tp1_armed:bool=False

class PaperTrader:
    def __init__(self, db, s):
        self.db=db; self.s=s; self.cash=s.start_balance; self.positions={}
    def buy(self, mint, price, score, reason="signal"):
        price=float(price)
        if mint in self.positions or price<=0 or self.cash<self.s.position_size: return False
        n=self.s.position_size; q=n/price; self.cash-=n
        self.positions[mint]=Position(mint,q,price,n,score,price)
        self.db.log_trade(mint,"BUY",q,price,n,0,reason,score,self.cash)
        return True
    def sell(self, mint, price, reason):
        p=self.positions.get(mint)
        if not p: return False
        price=float(price); proceeds=p.qty*price; pnl=proceeds-p.notional; self.cash+=proceeds
        self.db.log_trade(mint,"SELL",p.qty,price,proceeds,pnl,reason,p.score,self.cash)
        del self.positions[mint]; return True
    def on_price(self, mint, price):
        p=self.positions.get(mint)
        if not p: return None
        price=float(price); p.highest_price=max(p.highest_price,price); pct=price/p.entry_price-1
        if pct<=self.s.stop_loss_pct: self.sell(mint,price,"STOP_LOSS"); return "STOP_LOSS"
        if pct>=self.s.tp2_pct: self.sell(mint,price,"TP2"); return "TP2"
        if pct>=self.s.tp1_pct: p.tp1_armed=True
        if p.tp1_armed and price<=p.highest_price*(1-self.s.trailing_stop_pct):
            self.sell(mint,price,"TRAILING_STOP"); return "TRAILING_STOP"
        return None
    def equity(self, prices=None):
        prices=prices or {}
        return self.cash + sum(p.qty*float(prices.get(m,p.entry_price)) for m,p in self.positions.items())
