from config import settings
from database.db import Database
db=Database(settings.database_path)
print("\nLAST SIGNALS")
for r in db.c.execute("SELECT mint,score,decision,age_sec,trades,buy_sell_ratio,buyers,momentum FROM signals ORDER BY id DESC LIMIT 20"):
 print(dict(r))
print("\nPAPER TRADES")
for r in db.c.execute("SELECT mint,side,price,pnl,reason FROM paper_trades ORDER BY id DESC LIMIT 20"):
 print(dict(r))
