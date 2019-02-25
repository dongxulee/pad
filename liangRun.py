import sys
sys.path.insert(0, 'include')
import shift
import time

# Loading the tickers from Dow Jones
# test git
file = open("DowJonesTickers.pickle",'rb')
tickers = pickle.load(file)
print(tickers)

import numpy as np
import pandas as pd
import shift
import sys
import time
import statsmodels.api as sm
import matplotlib.pyplot as plt
from collections import defaultdict


# get stock list from universe


trader = shift.Trader('pad')
stock_list = trader.getStockList()
price_record = defaultdict(list)


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
