import backtrader as bt

class TestStrategy(bt.Strategy):
    def next(self):
        print(f"{self.datas[0].datetime.datetime(0)} - Close: {self.datas[0].close[0]}")
        if not self.position:
            self.buy()
        else:
            self.sell()

cerebro = bt.Cerebro()
cerebro.addstrategy(TestStrategy)

store = bt.stores.IBStore(host='127.0.0.1', port=7497, clientId=1)

data = store.getdata(dataname='AAPL-STK-SMART-USD', timeframe=bt.TimeFrame.Ticks)
cerebro.adddata(data)

broker = store.getbroker()
cerebro.setbroker(broker)

cerebro.run()