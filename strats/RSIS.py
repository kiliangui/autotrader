import backtrader as bt
from .globalStrat import GlobalStrategy

class RSIStrategy(GlobalStrategy):
    params = (
        ('bollinger_width_max', 0.06),
        ('take_profit_boost', 1.02),
        ('stop_loss_pct', 0.02),      # Added
        ('take_profit_pct', 0.15),    # Added
    )

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        if trade.pnl > 0:
            self.wins += 1
            #self.log("+ " + str(abs(trade.pnl)))
        else:
            self.losses += 1
            #self.log("- " + str(abs(trade.pnl)))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Order submitted/accepted to broker - nothing to do yet
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED: Price: {order.executed.price:.2f}, Size: {order.executed.size}")
                self.entry_price = order.executed.price
            elif order.issell():
                print("SELL EXECUTED")
                if order.exectype == bt.Order.Limit:
                    pass
                    #self.log(f"TAKE PROFIT HIT: Price: {order.executed.price:.2f}, Size: {order.executed.size}")
                elif order.exectype == bt.Order.Stop:
                    print("STOPLOSS")
                    self.log(f"STOP LOSS HIT: Price: {order.executed.price:.2f}, Size: {order.executed.size}")

        elif order.status in [ order.Margin, order.Rejected]:
            self.log(f"ORDER CANCELLED/MARGIN/REJECTED: {order.Status[order.status]}")
    def __init__(self):
        super().__init__()
        self.downSMA = {}
        self.firstSMA = {}
        self.secondSMA = {}
        self.position_bar = None  # Track when position was opened
        self.order = None
        self.tp_order = None
        self.st_order = None
        self.wins = 0
        self.losses = 0

        for data in self.datas:
            self.downSMA[data] = bt.indicators.EMA(data.close, period=200)
            self.firstSMA[data] = bt.indicators.EMA(data.close, period=34)
            self.secondSMA[data] = bt.indicators.EMA(data.close, period=7)

    def next(self):
        for data in self.datas:
            downSMA = self.downSMA[data]
            firstSMA = self.firstSMA[data]
            secondSMA = self.secondSMA[data]

            

            if (self.order and len(self.order) == 1):
                if(self.order[0].status==4):
                    self.order=None
            # Bearish crossover: close position + cancel orders
            pos = self.getposition(data)
            # Check if we already have a position
            if pos and pos.size > 0:
                if (firstSMA[-1] < secondSMA[-1]) and (firstSMA[0] > secondSMA[0]):

                    if self.order and len(self.order) >=0:
                        print("Bearish crossover - closing position and cancelling orders"+str(len(self.order)))
                        isclosing = 0
                        for o in self.order:
                            if (o.exectype == bt.Order.Stop):
                                if (o.price <= data.low[0]):
                                    isclosing=1
                                    return
                        if (not isclosing):
                            for o in self.order:
                                self.broker.cancel(o)
                                
                        o1 = self.sell(data=data,size=pos.size)
                        self.order = [o1]
                        print("Selling the position")
                        self.order = None

            # If we have open orders, do nothing
            if pos:
                return

            # Buy conditions
            if (data.low[0] > downSMA[0] and
                firstSMA[0] > downSMA[0] and
                secondSMA[0] > downSMA[0]):

                # Bullish crossover
                if (firstSMA[-1] > secondSMA[-1]) and (firstSMA[0] < secondSMA[0]):

                    if not pos:
                        entry_price = data.close[0]
                        stop_loss_price = entry_price * (1 - self.params.stop_loss_pct)
                        take_profit_price = entry_price * (1 + .12)

                        cash = self.broker.getcash()
                        print("CASH : "+str(cash)+"$")
                        size = int(cash / entry_price)


                        if size >= 1:

                          # Entry order
                            o1 = self.buy(
                                data=data,
                                size=size,
                                price=entry_price,
                                transmit=False
                            )

                            # First Take-Profit limit order (half size)
                            o3 = self.sell(
                                data=data,
                                price=take_profit_price,
                                size=size,
                                exectype=bt.Order.Limit,
                                parent=o1,
                                transmit=False
                            )

                            # First Stop-Loss if first TP not reached
                            o2 = self.sell(
                                data=data,
                                size=size,
                                exectype=bt.Order.Stop,
                                price=stop_loss_price,
                                parent=o1,
                                transmit=True
                            )

                         
                            self.order = [o1, o2, o3]
