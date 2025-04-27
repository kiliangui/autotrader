
import math
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
            self.entry = None
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
                print('entry',order.executed.size,order.executed.price)
                self.entry=order.executed.price
            elif order.issell():
                #self.log('SELL EXECUTED, %.2f' % order.executed.price)
                print(order.executed.size,order.executed.price)
                value = (order.executed.price-self.entry)*abs(order.executed.size)
                if value > 0:
                    self.log("+ : %.2f , cash  : %.2f" % (value, self.broker.getcash()))
                else:
                    self.log("- : %.2f, cash  : %.2f" % (value, self.broker.getcash()))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            #self.log('Order Canceled/Margin/Rejected')
            self.order = None
        #else:
            #self.log("ORDER STATUS NOT FOUND : "+order.status)
        self.order = None
    def next(self):
        self.log("NOT IMPLEMENTED")
        

class CrossingSMAStrategy(GlobalStrategy):
    params=(('bollinger_width_max', 0.06),     # Threshold for "wide" bands
        ('take_profit_boost', 1.02))
    def __init__(self):
        super().__init__()
        print("initialyzing strategy")
        self.downSMA = {}
        self.firstSMA = {}
        self.secondSMA = {}
        self.position_bar = None  # Track when position was opened
        self.rsi = {}
        self.order_main = None
        self.tp_orders = []
        self.sl_order = None

        for data in self.datas:
            self.downSMA[data] = bt.indicators.EMA(data.close, period=200)
            self.firstSMA[data] = bt.indicators.EMA(data.close, period=34)
            self.secondSMA[data] = bt.indicators.EMA(data.close, period=7)
            self.rsi[data] = bt.indicators.RSI(data.close, period=14)
    def notify_order(self, order):
            if order.status in [bt.Order.Completed]:
                if order.isbuy():
                    print(f"[FILLED] Buy @ {order.executed.price:.2f}")
                elif order.issell():
                    print(f"[FILLED] Sell @ {order.executed.price:.2f} ")
                    if order.exectype == bt.Order.Limit:
                        print("TP")
                    elif order.exectype == bt.Order.Stop:
                        print("STOP")
                    if order == self.sl_order:
                        print(">> Stop loss hit. Cancelling take profits.")
                        for o in self.tp_orders:
                            self.cancel(o)
                        self.order_main = None
                        self.tp_orders = []
                        self.sl_order = None
                    elif order in self.tp_orders:
                        print(">> One take profit hit.")
                        self.tp_orders = [o for o in self.tp_orders if not o.executed]
                        if not self.tp_orders and self.sl_order:
                            self.cancel(self.sl_order)
                            self.order_main = None
                            self.tp_orders = []
                            self.sl_order = None
                        if len(self.tp_orders) > 0 and self.sl_order and self.sl_order.status != bt.Order.Completed:
                            # Set stop loss to the last take profit price (break-even or higher)
                            new_sl_price = order.executed.price  # Using the last TP price
                            print(f"[UPDATE SL] Updating stop loss to {new_sl_price:.2f}")
                            
                            # Cancel and update stop loss
                            size = self.sl_order.size
                            #self.cancel(self.sl_order)
                            #self.sl_order = self.sell(price=new_sl_price, size=size-order.executed.size, exectype=bt.Order.Stop)

                            

            elif order.status in [bt.Order.Canceled, bt.Order.Rejected]:
                #print(f"[ORDER] Canceled or Rejected:")
                pass
    def next(self):        
        if self.position:
            # Track how many bars we've held the position
            if (self.position_bar):
                bars_held = len(self) - self.position_bar

                if bars_held > 2:
                    self.sell(parent=self.order,transmit=False)
                    self.order = None
                    
                    self.position_bar = None
                
        

        for data in self.datas:             
            downSMA = self.downSMA[data]
            firstSMA = self.firstSMA[data]
            secondSMA = self.secondSMA[data]
            if data.low[0] > downSMA and (firstSMA > downSMA and secondSMA > downSMA):
                
                # detect secondSMA getting over firstSMA
                if (firstSMA[-1] > secondSMA[-1]) and (firstSMA[0] < secondSMA[0]):

            # Detect crossover
                    for data2 in self.datas:
                        if self.getposition(data2):
                            return
                    entry_price = data.close[0]
                    stop_loss_price = entry_price * (1 - self.params.stop_loss_pct)
                    take_profit_price = entry_price * (1 + self.params.take_profit_pct)
                    cash = self.broker.getcash()
                    if (cash > 2000.0):
                        cash = 2000.0
                    size = int(cash / entry_price)
                    if size >= 1 and self.order_main is None:
                        price = self.data.close[0]

                        # Place market order to buy
                        self.order_main = self.buy(size=size)
                        
                        # Manually submit 2 TP and 1 SL orders
                        tp1_price = entry_price * (1 + self.params.take_profit_pct)
                        tp2_price = entry_price * (1 + self.params.take_profit_pct+0.2)
                        sl_price = price * (1+self.params.stop_loss_pct)

                        # Split the position in two
                        self.tp_orders.append(self.sell(price=tp1_price, size=size // 2, exectype=bt.Order.Limit))
                        
                        self.tp_orders.append(self.sell(price=tp2_price, size=size // 2, exectype=bt.Order.Limit,parent=self.tp_orders[0],transmit=True))
                        self.sl_order = self.sell(price=sl_price-100, size=size, exectype=bt.Order.Stop)
                        