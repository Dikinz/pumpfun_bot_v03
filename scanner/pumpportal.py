import asyncio, json, random, websockets
BASE="wss://pumpportal.fun/api/data"

class PumpPortalScanner:
    def __init__(self, s, on_new_token, on_trade):
        self.s=s; self.on_new_token=on_new_token; self.on_trade=on_trade
    def url(self):
        return f"{BASE}?api-key={self.s.pumpportal_api_key}" if self.s.pumpportal_api_key else BASE
    async def run(self):
        backoff=2
        while True:
            try:
                async with websockets.connect(self.url(), ping_interval=20, ping_timeout=20) as ws:
                    print("[WS] Connected")
                    await ws.send(json.dumps({"method":"subscribeNewToken"}))
                    backoff=2
                    async for raw in ws:
                        try: d=json.loads(raw)
                        except Exception: continue
                        mint=d.get("mint"); typ=(d.get("txType") or "").lower()
                        if mint and typ in {"create","creation"}: await self.on_new_token(d)
                        elif mint and typ in {"buy","sell"}: await self.on_trade(d)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"[WS] {e}; reconnect {backoff}s")
                await asyncio.sleep(backoff); backoff=min(backoff*2,30)

async def demo_trades(mint, on_trade, start_mc=20, count=18):
    mc=max(float(start_mc or 20),1); buyers=[f"demo-wallet-{i}" for i in range(1,10)]
    for i in range(count):
        await asyncio.sleep(.35)
        buy = i<12 or random.random()>.55
        typ="buy" if buy else "sell"
        mc=max(1, mc*(1+(random.uniform(.01,.06) if buy else -random.uniform(.005,.035))))
        await on_trade({"mint":mint,"txType":typ,"traderPublicKey":random.choice(buyers),
                        "solAmount":random.uniform(.03,.3),"tokenAmount":random.uniform(1000,50000),
                        "marketCapSol":mc,"signature":f"demo-{mint[:6]}-{i}"})
