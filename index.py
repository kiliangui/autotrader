import yfinance as yf
import backtrader.feeds as btfeeds
import math
import backtrader as bt
from datetime import datetime, timedelta
from strats.Bullish import BullishEngulfingStrategy
from strats.Crossing import CrossingSMAStrategy
import sys
sys.setrecursionlimit(100000)
indice="GOLD"

# Create a Stratey

def GetData(indice, data, params,yahoo):
    #for d in data:
    #    d.columns = d.columns.get_level_values(0)  # Flatten yfinance multi-index

    cerebro = bt.Cerebro()
    for d in data:
        data_bt = None
        if (yahoo):
            data_bt = bt.feeds.PandasData(dataname=d)
        else:
            data_bt=d
        print("adding data")
        
        #cerebro.adddata(data_bt)
        cerebro.resampledata(
           data_bt,
           timeframe=bt.TimeFrame.Minutes,
           compression=120  # make it 5-minute bars
       )
    cerebro.addstrategy(CrossingSMAStrategy)
    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.005)
    print("RUNNING CEREBRO")
    
    strategies = cerebro.run()
    print("CEREBRO RUNNED")
    final_value = cerebro.broker.getvalue()
    if (len(data)<40):
        cerebro.plot(style="line")
        pass
    print(f'{indice}: Final Balance = ${cerebro.broker.getvalue()}')
    return {
        'symbol': indice,
        'final_balance': final_value,
        'win_rate': win_rate,
        'params': params,
        'wins': strat.wins,
        'losses': strat.losses
    }

# Parameters to optimize
stock_codes = ["AAPL", "NVDA"]
#periods = [ 300]  # → [100, 150, 200, 250, 300] → 5 values
#take_profit_pcts = [0.025]  # → 3 values
#stop_loss_pcts = [ 0.02]   # → 3 values
#rsi_periods = [14]             # → 3 values
#rsi_supers = [55]              # → 3 values
#print(len(periods))
#periods = [200, 250, 300]  # → [100, 150, 200, 250, 300] → 5 values
#take_profit_pcts = [0.02,0.025,0.03,0.05]  # → 3 values
#stop_loss_pcts = [0.005, 0.01, 0.02]   # → 3 values
#rsi_periods = [6,10,14,20]             # → 3 values
#rsi_supers = [55,65,69]   
#above_sma=[0,0.03] 
import os
import random

folder_path = './data'

# List all files in the folder
files = os.listdir(folder_path)

# Filter out directories (keep only files)
files = [f for f in files if os.path.isfile(os.path.join(folder_path, f))]

# Pick 4 random files
stock_codes = random.sample(files, 8)

print(stock_codes)
#stock_codes=[
#    "CERA",'ZEEL',"WHIRLPOOL","WIPRO","VINATIORGA","TITAN","SUPRAJIT","TANLA"
#  ]    
periods=[26]
take_profit_pcts = [0.1]
stop_loss_pcts = [ 0.02]  
rsi_periods = [12]     
rsi_supers = [55]         

# Print length of each hyperparameter range
print("Lengths of hyperparameter ranges:")
print(f"periods: {len(periods)}")
print(f"take_profit_pcts: {len(take_profit_pcts)}")
print(f"stop_loss_pcts: {len(stop_loss_pcts)}")
print(f"rsi_periods: {len(rsi_periods)}")
print(f"rsi_supers: {len(rsi_supers)}")
print(f"stock_codes: {len(stock_codes)}")

# Calculate total number of combinations per stock
total_combinations = (
    len(periods)
    * len(take_profit_pcts)
    * len(stop_loss_pcts)
    * len(rsi_periods)
    * len(rsi_supers)
)

# Total runs = combinations × number of stocks
total_runs = total_combinations * len(stock_codes)

print("\nTotal combinations per stock:", total_combinations)
print("Total runs across all stocks:", total_runs)


# Run and store results
results = {}
code="GOLD"
end_date = datetime.now()
start_date = end_date - timedelta(days=365*3)
data = []


print(data)
interval = "1h"
days =365
if (interval=="30m" or interval=="15m" or interval=="5m" or interval=="1m"):
    take_profit_pcts = [0.0454]
    stop_loss_pcts = [ 0.02]  
    days =28
if (interval=="1d"  or interval=="1h"):
    days=365
    take_profit_pcts = [0.05]
    stop_loss_pcts = [ 0.015]  

for code in stock_codes:
    print(f"\nFetching data for {code}...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    #data.append(yf.download(code, start=start_date, end=end_date,group_by='ticker',multi_level_index=False,interval=interval))
    data.append(btfeeds.GenericCSVData(
   dataname='./data/'+code,
   nullvalue=0.0,

   timeframe=bt.TimeFrame.Minutes,
   compression=15,  # 1 minute
   datetime=0,
   open=1,
   high=2,
   low=3,
   close=4,
   volume=5,
   openinterest=-1))
    
    #if data[-1].empty:
    #   print(f"Skipping {code}, no data found.")
if False:
    GetData(code,data,{
                            'period': 200,
                            'take_profit_pct': 0.02,
                            'stop_loss_pct': 0.01,
                            'rsi_period': 14,
                            'rsi_super': 55
                        })
else:
    for period in periods:
        print(period,periods[-1])
        for tp in take_profit_pcts:
            for sl in stop_loss_pcts:
                for rsi_period in rsi_periods:
                    for rsi_super in rsi_supers:
                        params = {
                            'period': period,
                            'take_profit_pct': tp,
                            'stop_loss_pct': sl,
                            'rsi_period': rsi_period,
                            'rsi_super': rsi_super
                        }
                        result = GetData(code, data, params,False)
                        key = f"{period}-{tp}-{sl}-{rsi_period}-{rsi_super}"
                        if (key in results.keys()):
                            result["final_balance"] += results[key]["final_balance"]
                            result["win_rate"] += results[key]["win_rate"]
                            result["wins"] += results[key]["wins"]
                            result["losses"] += results[key]["losses"]
                            result["win_rate"] = result["wins"]/result["losses"]
                            results[key] = result
                        else:
                            results[key] = result
# Sort results by best win rate
sorted_results = sorted(results.values(), key=lambda x: x['win_rate'], reverse=False)

# Print top 5
print("\nTop 5 strategies:")
for res in sorted_results[:5]:
    print(res)
