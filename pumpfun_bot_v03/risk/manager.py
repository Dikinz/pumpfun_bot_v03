class RiskManager:
    def __init__(self, s):
        self.s=s; self.start=s.start_balance
    def can_open(self, cash, open_positions):
        if cash < self.s.position_size: return False, "insufficient cash"
        if cash <= self.s.emergency_balance: return False, "emergency balance reached"
        if open_positions >= self.s.max_positions: return False, "max positions reached"
        if max(0,self.start-cash) >= self.start*self.s.daily_max_loss_pct: return False, "daily loss limit reached"
        return True, "ok"
