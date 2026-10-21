from dataclasses import dataclass

@dataclass
class ScoreResult:
    score: int
    reason: str

def score_token(r, s):
    if not r:
        return ScoreResult(0, "no token data")
    trades=int(r["trade_count"] or 0); buys=int(r["buy_count"] or 0); sells=int(r["sell_count"] or 0)
    buyers=int(r["unique_buyers"] or 0); mc=float(r["last_market_cap_sol"] or 0)
    initial_mc=float(r["market_cap_sol"] or 0); initial_buy=float(r["initial_buy"] or 0)
    score=0; reasons=[]
    if trades >= s.min_trades_for_entry: score+=15; reasons.append("trades +15")
    if buys/max(sells,1) >= s.min_buy_sell_ratio: score+=20; reasons.append("buy/sell +20")
    if buyers >= s.min_unique_buyers: score+=15; reasons.append("buyers +15")
    if mc >= s.min_market_cap_sol: score+=10; reasons.append("min mc +10")
    if s.min_market_cap_sol <= mc <= s.max_market_cap_sol: score+=10; reasons.append("mc range +10")
    if initial_mc > 0 and mc > initial_mc: score+=15; reasons.append("momentum +15")
    if 0 <= initial_buy <= s.max_creator_initial_buy: score+=10; reasons.append("creator buy +10")
    return ScoreResult(min(score,100), ", ".join(reasons) or "no positive factors")
