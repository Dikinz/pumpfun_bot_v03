class RiskManager:
    def __init__(self,s):
        self.s=s;self.start=s.start_balance
    def can_open(self,cash,open_positions,equity):
        if cash<self.s.position_size:return False,"insufficient cash"
        if open_positions>=self.s.max_positions:return False,"max positions reached"
        if equity<=self.s.emergency_balance:return False,"emergency equity threshold reached"
        loss=max(0.0,self.start-equity)
        if loss>=self.start*self.s.daily_max_loss_pct:return False,"daily equity loss limit reached"
        return True,"ok"
