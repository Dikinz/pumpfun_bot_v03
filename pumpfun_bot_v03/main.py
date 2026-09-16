import asyncio
from config import settings
from database.db import Database
from strategy.scorer import score_token
from risk.manager import RiskManager
from trading.paper import PaperTrader
from scanner.pumpportal import PumpPortalScanner, demo_trades

db=Database(settings.database_path); risk=RiskManager(settings); trader=PaperTrader(db,settings)
observed=set(); latest={}

async def evaluate(mint):
    await asyncio.sleep(settings.observation_seconds)

    r = db.get_token(mint)
    s = score_token(r, settings)

    decision = "BUY" if s.score >= settings.min_score else "NO_BUY"

    db.log_signal(
        mint,
        s.score,
        decision,
        s.reason
    )

    print(
        f"[SCORE] {mint[:8]} "
        f"{s.score} {decision} | {s.reason}"
    )

    if decision == "BUY":
        current_equity = trader.equity(latest)

        ok, why = risk.can_open(
            trader.cash,
            len(trader.positions),
            current_equity
        )

        if not ok:
            db.log_signal(
                mint,
                s.score,
                "BLOCKED",
                why
            )
            print("[RISK]", why)
            return

        price = float(
            r["last_market_cap_sol"]
            or r["market_cap_sol"]
            or 0
        )

        if price > 0:
            opened = trader.buy(
                mint,
                price,
                s.score,
                "score entry"
            )

            if opened:
                current_equity = trader.equity(latest)

                print(
                    f"[PAPER BUY] {mint[:8]} "
                    f"proxy={price:.4f} "
                    f"position=${settings.position_size:.2f} "
                    f"cash=${trader.cash:.2f} "
                    f"equity=${current_equity:.2f} "
                    f"pnl=${current_equity-settings.start_balance:+.2f}"
                )

async def on_new(d):
    mint=d.get("mint")
    if not mint: return
    mc=d.get("marketCapSol") or 0; creator=d.get("traderPublicKey") or d.get("creator","")
    db.upsert_token(mint,d.get("symbol",""),d.get("name",""),creator,d.get("initialBuy") or d.get("solAmount") or 0,mc)
    db.log_event(mint,"create",d,d.get("signature",""),creator,d.get("solAmount",0),d.get("tokenAmount",0),mc)
    print(f"[NEW] {d.get('symbol','?')} {mint[:8]} mc={float(mc or 0):.2f}")
    if mint not in observed:
        observed.add(mint); asyncio.create_task(evaluate(mint))
        if settings.demo_trade_feed: asyncio.create_task(demo_trades(mint,on_trade,mc or 20))

async def on_trade(d):
    mint=d.get("mint")
    if not mint: return
    side=(d.get("txType") or "").lower(); who=d.get("traderPublicKey") or ""; mc=float(d.get("marketCapSol") or 0)
    db.log_event(mint,"trade",d,d.get("signature",""),who,d.get("solAmount",0),d.get("tokenAmount",0),mc)
    db.update_trade_stats(mint,side,who,mc)
    if mc>0:
        latest[mint]=mc; action=trader.on_price(mint,mc)
        if action: print(f"[EXIT] {mint[:8]} {action} proxy={mc:.4f} cash=${trader.cash:.2f}")

async def snapshots():
    while True:
        await asyncio.sleep(10)
        eq=trader.equity(latest); db.snapshot(trader.cash,eq,len(trader.positions))
        print(f"[PORTFOLIO] cash=${trader.cash:.2f} equity=${eq:.2f} open={len(trader.positions)}")

async def main():
    print("Pump.fun Bot v0.3 — PAPER MODE")
    print(f"Start ${settings.start_balance:.2f}; position ${settings.position_size:.2f}; demo={settings.demo_trade_feed}")
    print("marketCapSol is a paper-test proxy, not executable price.")
    sc=PumpPortalScanner(settings,on_new,on_trade)
    await asyncio.gather(sc.run(),snapshots())

if __name__=="__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("Stopped.")
