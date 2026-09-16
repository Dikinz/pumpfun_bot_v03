from types import SimpleNamespace
from database.db import Database
from trading.paper import PaperTrader

def test_paper(tmp_path):
    s=SimpleNamespace(start_balance=30.0,position_size=5.0,stop_loss_pct=-.12,tp1_pct=.20,tp2_pct=.40,trailing_stop_pct=.10)
    db=Database(str(tmp_path/"t.db"))
    db.upsert_token("m","T","Test","c",1,10)
    t=PaperTrader(db,s)
    assert t.buy("m",10,80)
    assert round(t.cash,2)==25
    assert t.sell("m",12,"x")
    assert round(t.cash,2)==31
