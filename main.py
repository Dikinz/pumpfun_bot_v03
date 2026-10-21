import asyncio,math,time
from config import settings
from database.db import Database
from scanner.pumpportal import PumpPortal
from strategy.scorer import score,entry_gates
from strategy.watchlist import candidate_rank
from risk.manager import RiskManager
from trading.paper import PaperTrader
db=Database(settings.database_path);paper=PaperTrader(db,settings);risk=RiskManager(settings);latest={};portal=None;rank_evictions=0
def num(v):
 try:return float(v)
 except:return 0.0
def derive(d):
 sol=num(d.get("solAmount"));tok=num(d.get("tokenAmount"));p=sol/tok if sol>0 and tok>0 else 0
 return sol,tok,p,math.isfinite(p) and p>0
def momentum(m):
 x=db.recent_prices(m,8)
 if len(x)<settings.min_price_samples or x[0]<=0:return 0.0,len(x)
 return x[-1]/x[0]-1,len(x)
async def evaluate(m):
 await asyncio.sleep(settings.observation_seconds)
 if m not in portal.watched and m not in paper.positions:return
 r=db.token(m)
 if not r:return
 mom,samples=momentum(m);buyers=db.buyers(m);ratio=r["buy_count"]/max(r["sell_count"],1);age=time.time()-r["created_ts"]
 gate_ok,gate=entry_gates(r,buyers,mom,samples,age,settings);sc,why=score(r,buyers,mom,settings)
 p=db.last_price(m);dec="BUY" if gate_ok and sc>=settings.min_score else "NO_BUY"
 db.signal(m,sc,dec,why,p or 0,age,r["trade_count"],ratio,buyers,mom,gate)
 print(f"[SIGNAL] {m[:8]} score={sc} {dec} gate={gate} age={age:.0f}s trades={r['trade_count']} ratio={ratio:.2f} buyers={buyers} mom={mom:+.1%} samples={samples} | {why}")
 if dec=="BUY":
  ok,msg=risk.can_open(m,paper.cash,len(paper.positions),paper.equity(latest))
  if not ok:print("[RISK]",msg);return
  metrics=db.candidate_metrics(m) or {}
  entry_meta={"score":sc,"age":age,"trades":r["trade_count"],"ratio":ratio,"buyers":buyers,"momentum":mom,"mc":r["last_mc"],"samples":samples,"rank":candidate_rank(metrics,settings) if metrics else 0}
  if p and paper.buy(m,p,entry_meta):
   latest[m]=p
   print(f"[PAPER BUY] {m[:8]} priceSOL={p:.12g} size=${settings.position_size:.2f} cash=${paper.cash:.2f} score={sc} trades={r['trade_count']} ratio={ratio:.2f} buyers={buyers} mom={mom:+.1%} rank={entry_meta['rank']:.1f}")
async def expire(m):
 await asyncio.sleep(settings.dead_token_seconds)
 r=db.token(m)
 if m not in paper.positions and r and r["trade_count"]==0:
  await portal.unsubscribe(m,"no trades timeout")
  return
 await asyncio.sleep(max(0,settings.watch_seconds-settings.dead_token_seconds))
 if m not in paper.positions:await portal.unsubscribe(m,"watch timeout")
async def on_new(d):
 m=d.get("mint");mc=num(d.get("marketCapSol"))
 if not m:return
 db.new(m,d.get("symbol","?"),mc);print(f"[NEW] {d.get('symbol','?')} {m[:8]} mcSOL={mc:.2f}")
 # FREE GATE: reject obvious out-of-range launches before opening a paid token-trade subscription.
 initial_buy=num(d.get("solAmount") or d.get("initialBuy") or 0)
 free_ok=(settings.free_min_market_cap_sol<=mc<=settings.free_max_market_cap_sol and initial_buy>=settings.free_min_initial_buy_sol)
 if not free_ok:
  print(f"[FREE DROP] {m[:8]} mcSOL={mc:.2f} initialSOL={initial_buy:.4f}")
  return
 if settings.api_key:
  if len(portal.watched)>=settings.max_watched_tokens:
   victim=None;victim_rank=10**9
   for w in list(portal.watched):
    if w in paper.positions:continue
    x=db.candidate_metrics(w)
    if x and x["age"]>=settings.watchlist_min_age_seconds:
     rr=candidate_rank(x,settings)
     if rr<victim_rank:victim,victim_rank=w,rr
   new_rank=candidate_rank(db.candidate_metrics(m),settings)
   if victim and ((db.candidate_metrics(victim) or {}).get("trades",0)<2 or new_rank>=victim_rank+settings.watchlist_evict_margin):
    global rank_evictions;rank_evictions+=1
    print(f"[RANK EVICT] {victim[:8]} rank={victim_rank:.1f} -> {m[:8]} rank={new_rank:.1f}")
    await portal.unsubscribe(victim,"rank replacement")
  if len(portal.watched)<settings.max_watched_tokens:
   subscribed=await portal.subscribe(m)
   if subscribed:asyncio.create_task(evaluate(m));asyncio.create_task(expire(m))
async def on_trade(d):
 m=d.get("mint");side=(d.get("txType") or "").lower();mc=num(d.get("marketCapSol"));sol,tok,p,valid=derive(d);prev=db.last_price(m)
 if valid and prev and (p/prev>settings.max_price_jump_ratio or prev/p>settings.max_price_jump_ratio):valid=False
 db.event(m,side,d.get("traderPublicKey",""),mc,sol,tok,p,valid,d)
 if valid:
  latest[m]=p;res=paper.on_price(m,p)
  if res:
   reason,pnl,mfe,mae,holding=res;risk.exited(m);print(f"[EXIT] {m[:8]} {reason} pnl=${pnl:+.2f} MFE={mfe:+.1%} MAE={mae:+.1%} hold={holding:.1f}s realized=${paper.realized:+.2f}");await portal.unsubscribe(m,"position closed")
async def status():
 while True:
  await asyncio.sleep(settings.snapshot_seconds);st=db.stats();ex=st["exits"] or 0;wr=100*st["wins"]/ex if ex else 0
  print(f"[PORTFOLIO] cash=${paper.cash:.2f} equity=${paper.equity(latest):.2f} realized=${paper.realized:+.2f} open={len(paper.positions)} exits={ex} winrate={wr:.1f}% maxDD={paper.max_dd:.1%}")
  print(f"[STREAM] {portal.diagnostics()} rank_evictions={rank_evictions}")
async def main():
 global portal
 print("Pump.fun Bot v0.4.4.4 COST OPTIMIZER — PAPER ONLY")
 portal=PumpPortal(settings,on_new,on_trade);await asyncio.gather(portal.run(),status())
if __name__=="__main__":
 try:asyncio.run(main())
 except KeyboardInterrupt:print("\nStopped")
