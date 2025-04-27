
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
        self.order = None
        self.tp_order = None
        self.st_order = None

        for data in self.datas:
            self.downSMA[data] = bt.indicators.EMA(data.close, period=200)
            self.firstSMA[data] = bt.indicators.EMA(data.close, period=34)
            self.secondSMA[data] = bt.indicators.EMA(data.close, period=7)
            
    def next(self):
        for data in self.datas:
            downSMA = self.downSMA[data]
            firstSMA = self.firstSMA[data]
            secondSMA = self.secondSMA[data]
            
            # Check if we already have a position
            pos = self.getposition(data)
            
            # Bearish crossover: close position + cancel orders
            if pos:
                if (firstSMA[-1] < secondSMA[-1]) and (firstSMA[0] > secondSMA[0]):
                    print("Bearish crossover - closing position and cancelling orders")
                    
                    # Cancel open orders if any
                    if self.order:
                        for o in self.order:
                            self.broker.cancel(o)
                        self.order = None
                    
                    # Sell current position
                        self.sell(data=data, size=pos.size)
            
            # If we have open orders, do nothing
            if self.order:
                return
            
            # Buy conditions
            if data.low[0] > downSMA and (firstSMA[0] > downSMA and secondSMA[0] > downSMA):
                
                # Bullish crossover
                if (firstSMA[-1] < secondSMA[-1]) and (firstSMA[0] > secondSMA[0]):
                    
                    # No position yet
                    if not pos:
                        entry_price = data.close[0]
                        stop_loss_price = entry_price * (1 - self.params.stop_loss_pct)
                        take_profit_price = entry_price * (1 + self.params.take_profit_pct)
                        
                        cash = self.broker.getcash()
                        if cash > 2000.0:
                            cash = 2000.0
                        
                        size = int(cash / entry_price)
                        print(f"Buying {size} units at {entry_price}")
                        
                        if size >= 1:
                            self.order = self.buy_bracket(
                                data=data,
                                size=size,
                                price=entry_price,            # Entry
                                limitprice=take_profit_price,  # Take profit
                                stopprice=stop_loss_price      # Stop loss
                            )