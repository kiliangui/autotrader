
import backtrader as bt
from .globalStrat import GlobalStrategy
class BullishEngulfingStrategy(GlobalStrategy):
    def __init__(self):
        super().__init__()
        self.rsi_by_data = {}
        self.ema_by_data = {}

        for data in self.datas:
            self.rsi_by_data[data] = bt.indicators.RSI(data.close, period=self.params.rsi_period)
            self.ema_by_data[data] = bt.indicators.EMA(data.close, period=self.params.period)
    def next(self):
        if self.order:
            return

        for data in self.datas:
            rsi = self.rsi_by_data[data]
            ema = self.ema_by_data[data]

            last_open = data.open[0]
            last_close = data.close[0]
            prev_open = data.open[-1]
            prev_close = data.close[-1]

            is_bullish_engulfing = (
                prev_close < prev_open and
                last_close > last_open and
                last_open <= prev_close and
                last_close >= prev_open
            )

            if (
                data.low[0] > ema[0] and
                data.low[-1] > ema[-1] and
                rsi[0] > self.params.rsi_super and
                is_bullish_engulfing and
                not self.getposition(data)
            ):
                entry_price = data.open[0]
                take_profit_price = entry_price * (1 + self.params.take_profit_pct)
                stop_loss_price = entry_price * (1 - self.params.stop_loss_pct)

                cash = self.broker.getcash()
                size = int(cash / entry_price)

                if size >= 1:
                    self.log(f'BUY CREATE: {entry_price:.2f} (size={size})')

                    o1 = self.buy(data=data, size=size, exectype=bt.Order.Market, transmit=False)
                    o2 = self.sell(data=data, size=size, price=stop_loss_price,
                                   exectype=bt.Order.Stop, transmit=False, parent=o1)
                    o3 = self.sell(data=data, size=size, price=take_profit_price,
                                   exectype=bt.Order.Limit, transmit=True, parent=o1)

                    self.order = o1    