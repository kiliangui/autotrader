from datetime import datetime
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        print("Strategy")
    def next(self):
        print(f'{self.data.datetime.datetime(0)}: {self.data.close[0]}')

cerebro = bt.Cerebro()

# Live data feed using Interactive Brokers
from backtrader.feeds import IBData

data = IBData(
    dataname='AAPL-STK-SMART-USD',
    fromdate=datetime(2024, 4, 25),
    timeframe=bt.TimeFrame.Minutes,
    compression=15,
    clientId=1,
    host='127.0.0.1',
    port=7497,
    _debug=False,
    backfill_start=True,  # Optional: gets some history before live kicks in
)

cerebro.adddata(data)
cerebro.addstrategy(TestStrategy)

cerebro.run()