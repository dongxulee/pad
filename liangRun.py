import sys
sys.path.insert(0, 'include')
import numpy as np
import pandas as pd
import shift
import time
import matplotlib.pyplot as plt
from collections import defaultdict
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns


# 临时数据，请删除
aapl = pd.DataFrame([['aapl', 198], ['aapl', 209]], columns=['Name', 'Last'])
amzn = pd.DataFrame([['amzn', 2032], ['amzn', 2314]], columns=['Name', 'Last'])
portfolio = {'AAPL': aapl, 'AMZN': amzn}


# Setup trader for accumulating information
client_id_number = 6  # client ID number
verbose = 1
client_id = f"test{str(client_id_number).zfill(3)}"
trader = shift.Trader(client_id)


# Get data set from universe
hist_price = pd.DataFrame()
stock_list = trader.getStockList()
for symbol in ['AAPL', 'AMZN']:
    hist_price = pd.concat([hist_price, portfolio[symbol]['Last']], axis=1).rename(columns={'Last': symbol})

print(hist_price)

# Calculate expected returns and sample covariance
mu = expected_returns.mean_historical_return(hist_price)
S = risk_models.sample_cov(hist_price)


# Optimise for maximal Sharpe ratio
ef = EfficientFrontier(mu, S)
raw_weights = ef.max_sharpe()
cleaned_weights = ef.clean_weights()
print(cleaned_weights)
ef.portfolio_performance(verbose=True)


# linear regression


time_series = list(range(0,370,10))
avg_return = {}
for symbol in stock_list:
    y = price_record[symbol]
    # y = [1,2,3,4,5,6,7,8,12,11,10,14,16,23,15,17,19,17,22,25,27,24,29,31,30,32,27,26,36,40,42,45,32,39,47,56,50]
    x = sm.add_constant(time_series)
    est = sm.OLS(y, x).fit()
    b, a = est.params
    avg_return[symbol] = a * 360 / b



    # price_forecast = est.predict(x)
    # plt.scatter(x, y)
    # est.summary()


# scan for every 10 sec
elapsed_time = 0
time_counter1 = 0
interval = 10       # change the interval of data collection here

while True:

    # collecting information
    for symbol in stock_list:
        price_record[symbol].append(trader.getLastPrice(symbol))

    # Processing and command
    if time_counter1 >= 360:
        pass
        time_counter1 = 0

    # time record
    time.sleep(interval)
    elapsed_time = elapsed_time + interval
    time_counter1 = time_counter1 + interval
