from config import settings
from database.db import Database
db=Database(settings.database_path)
rows=db.c.execute("SELECT * FROM paper_trades WHERE side='SELL' ORDER BY id").fetchall()
wins=[r for r in rows if r["pnl"]>0];loss=[r for r in rows if r["pnl"]<=0]
gp=sum(r["pnl"] for r in wins);gl=-sum(r["pnl"] for r in loss)
def avg(a,k):return sum((r[k] or 0) for r in a)/len(a) if a else 0
def pct(x):return f"{x:+.1%}"
print("=== v0.4.4.3 STRATEGY ANALYZER / PAPER REPORT ===")
print(f"TRADES: {len(rows)} | WINS: {len(wins)} | LOSSES: {len(loss)} | WIN RATE: {(100*len(wins)/len(rows) if rows else 0):.1f}%")
for x in ("TP2","TRAILING_STOP","STOP_LOSS"):print(f"{x}: {sum(r['reason']==x for r in rows)}")
print(f"NET PNL: ${gp-gl:+.2f} | AVG WIN: ${avg(wins,'pnl'):+.2f} | AVG LOSS: ${avg(loss,'pnl'):+.2f} | PROFIT FACTOR: {(gp/gl if gl else float('inf')):.2f}")
print(f"AVG MFE: {pct(avg(rows,'mfe_pct'))} | AVG MAE: {pct(avg(rows,'mae_pct'))} | AVG HOLD: {avg(rows,'holding_sec'):.1f}s")
print("\nWINNERS vs LOSERS (entry snapshot)")
for label,a in (("WIN ",wins),("LOSS",loss)):
 print(f"{label}: n={len(a)} score={avg(a,'entry_score'):.1f} age={avg(a,'entry_age_sec'):.1f}s trades={avg(a,'entry_trades'):.1f} ratio={avg(a,'entry_ratio'):.2f} buyers={avg(a,'entry_buyers'):.1f} mom={pct(avg(a,'entry_momentum'))} mc={avg(a,'entry_mc'):.1f} samples={avg(a,'entry_samples'):.1f} rank={avg(a,'entry_rank'):.1f} MFE={pct(avg(a,'mfe_pct'))} MAE={pct(avg(a,'mae_pct'))} hold={avg(a,'holding_sec'):.1f}s")
print("\nEXIT BREAKDOWN")
for reason in ("TP2","TRAILING_STOP","STOP_LOSS"):
 a=[r for r in rows if r["reason"]==reason]
 if a:print(f"{reason}: n={len(a)} pnl=${sum(r['pnl'] for r in a):+.2f} avg=${avg(a,'pnl'):+.2f} MFE={pct(avg(a,'mfe_pct'))} MAE={pct(avg(a,'mae_pct'))} hold={avg(a,'holding_sec'):.1f}s")
print("\nGATE REJECTIONS:")
for x in db.c.execute("SELECT gate_reason,COUNT(*) n FROM signals WHERE decision='NO_BUY' GROUP BY gate_reason ORDER BY n DESC"):print(f"{x['gate_reason'] or 'score'}: {x['n']}")
print("\nSIGNAL QUALITY BY GATE:")
for x in db.c.execute("SELECT COALESCE(NULLIF(gate_reason,''),'score') gate,COUNT(*) n,ROUND(AVG(score),1) avg_score,ROUND(AVG(trades),1) avg_trades,ROUND(AVG(buy_sell_ratio),2) avg_ratio,ROUND(AVG(buyers),1) avg_buyers,ROUND(AVG(momentum)*100,2) avg_mom_pct FROM signals GROUP BY COALESCE(NULLIF(gate_reason,''),'score') ORDER BY n DESC"):
 print(f"{x['gate']}: n={x['n']} avg_score={x['avg_score']} trades={x['avg_trades']} ratio={x['avg_ratio']} buyers={x['avg_buyers']} mom={x['avg_mom_pct']}%")
