from ib_insync import *

# Connect to Interactive Brokers API
ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

# Define the contract for Apple Inc. stock
contract = Stock('AMZN', 'SMART','USD')

# Request market data
ib.reqMarketDataType(3)
ib.reqMktData(contract, '', False, False)
lminutes = 16
# Function to handle market data updates
def onPendingTickers(tickers):
    global lminutes
    e = next(iter(tickers))
    minutes = e.time.minute
    if (minutes%1==0 and lminutes != minutes):
        if (minutes%1==0 and lminutes != minutes):
            for ticker in tickers:
                print(f'{minutes},Ticker: {ticker.contract.symbol}, Last: {ticker.last}, Bid: {ticker.bid}, Ask: {ticker.ask}')
        lminutes=minutes
        print("MID Tick")
# Register the function to handle market data updates
ib.pendingTickersEvent += onPendingTickers

# Keep the script running to receive market data updates
ib.run()
#order = LimitOrder('SELL', 200, 1.11)
#trade = ib.placeOrder(contract, order)
#print(trade)
#
#def onStatusEvent(event):
#    print(event)
#
#ib.run()
#ib.orderStatusEvent += onStatusEvent


def MakeAnOrder(stock,price,size,tp,sl):
    contract = Stock(stock, 'SMART','USD')
    order= Order()
    trade = ib.placeOrder(contract=contract)
