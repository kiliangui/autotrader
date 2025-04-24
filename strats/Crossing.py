
import backtrader as bt
from .globalStrat import GlobalStrategy
class CrossingSMAStrategy(GlobalStrategy):
    params=(('bollinger_width_max', 0.06),     # Threshold for "wide" bands
        ('take_profit_boost', 1.02))
    def __init__(self):
        super().__init__()
        self.downSMA = {}
        self.firstSMA = {}
        self.secondSMA = {}
        self.position_bar = None  # Track when position was opened
        self.rsi = {}
        self.order = None

        for data in self.datas:
            self.downSMA[data] = bt.indicators.EMA(data.close, period=200)
            self.firstSMA[data] = bt.indicators.EMA(data.close, period=34)
            self.secondSMA[data] = bt.indicators.EMA(data.close, period=7)
            self.rsi[data] = bt.indicators.RSI(data.close, period=14)
            

    def next(self):

        
        if self.position:
            # Track how many bars we've held the position
            if (self.position_bar):
                bars_held = len(self) - self.position_bar

                if bars_held > 2:
                    self.sell(parent=self.order,transmit=False)
                    self.order = None
                    
                    self.position_bar = None
                
            
                


        if self.order:
            return

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
                    if size >= 1:
                        #self.log(f'CROSSOVER BUY: {entry_price:.2f} (TP={take_profit_price:.2f}, SL={stop_loss_price:.2f}, size={size})')
                        o1 = self.buy(data=data, size=size, exectype=bt.Order.Market, transmit=False)
                        o2 = self.sell(data=data, size=size, price=stop_loss_price,
                                    exectype=bt.Order.Stop, transmit=False, parent=o1)
                        o3 = self.sell(data=data, size=size, price=take_profit_price,
                                    exectype=bt.Order.Limit, transmit=True, parent=o1)
                        self.position_bar = len(self)
                        self.order = o1