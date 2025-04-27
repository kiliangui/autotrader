import pandas as pd
import numpy as np
from .globalStrat import GlobalStrategy
import backtrader as bt

class CrossingSMAStrategy(bt.Strategy):
    params = (
        ('fast', 20),
        ('slow', 34),
        ('_movav', bt.indicators.MovAv.SMA),
    )

    def __init__(self):
        # Store indicators for each data feed
        self.inds = dict()

        for i, d in enumerate(self.datas):
            sma_fast = self.p._movav(d, period=self.p.fast)
            sma_slow = self.p._movav(d, period=self.p.slow)
            sma_200 = self.p._movav(d, period=200)

            buysig = bt.indicators.CrossOver(sma_fast, sma_slow)

            self.inds[d] = dict(
                sma_fast=sma_fast,
                sma_slow=sma_slow,
                sma_200=sma_200,
                buysig=buysig,
            )

    def next(self):
        for d in self.datas:
            pos = self.getposition(d)
            isInPos = False
            for da in self.datas:
                if (self.getposition(da).size):
                    isInPos == True
            if pos.size>0:
                if self.inds[d]['buysig'][0] < 0:
                    self.sell(data=d)
            elif not isInPos:
                if self.inds[d]['buysig'][0] > 0 and d.close[0] > self.inds[d]['sma_200'][0]:
                    self.buy(data=d)
