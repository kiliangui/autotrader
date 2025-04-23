import backtrader as bt

class GlobalStrategy(bt.Strategy):
    params = (
        ('period', 200),
        ('take_profit_pct', 0.02),  # 2%
        ('stop_loss_pct', 0.006),    # 1%
        ('rsi_period',14),
        ('rsi_super',65)
    )
    def __init__(self):
            self.wins = 0
            self.losses = 0
            self.order = None
            self.entry_price = None
            self.take_profit_price = None
            self.stop_loss_price = None
            

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}, {txt}')
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        if trade.pnl > 0:
            self.wins += 1
        else:
            self.losses += 1
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None
    def next(self):
        self.log("NOT IMPLEMENTED")
        