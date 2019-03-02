import time
import pandas as pd
import shift
import sys
import numpy as np
sys.path.insert(0, 'include')
# if time%60==0

aapl = pd.DataFrame([['aapl', 198], ['aapl', 209],
                     ['aapl', 207], ['aapl', 210],
                     ['aapl', 208], ['aapl', 211],
                     ['aapl', 212], ['aapl', 216]], columns=['Name', 'Last'])
amzn = pd.DataFrame([['amzn', 2032], ['amzn', 2314],
                     ['amzn', 2024], ['amzn', 2335],
                     ['amzn', 2033], ['amzn', 2338],
                     ['amzn', 2040], ['amzn', 2342]], columns=['Name', 'Last'])
portfolio = {'AAPL': aapl, 'AMZN': amzn}

Trader = shift.trader()
tickers = Trader.getStockList()

def check_signal_bid(faker, Tickers, alpha): #alpha is using as a thresold
    delta = []
    for i in Tickers:
        bp = faker.getBestPrice(i)
        new = bp.getBidSize()
        sample_list = portfolio[i].BidSize
        index = [j for j in range(len(sample_list)) if (j+1)%5==0]
        data_ticker = []
        for k in index:
            data_ticker.append(sample_list[k])
        n = len(data_ticker)
        last = data_ticker[n-1]
        if new > alpha * last:
            delta.append((new - alpha * last)/(alpha * last))
        else:
            delta.append(0)
    return delta

def check_signal_ask(faker, Tickers, alpha):
    delta = []
    for i in Tickers:
        bp = faker.getBestPrice(i)
        new = bp.getAskSize()
        sample_list = portfolio[i].BidSize
        index = [j for j in range(len(sample_list)) if (j+1)%5==0]
        data_ticker = []
        for k in index:
            data_ticker.append(sample_list[k])
        n = len(data_ticker)
        last = data_ticker[n-1]
        if new > alpha * last:
            delta.append((new - alpha * last)/(alpha * last))
        else:
            delta.append(0)
    return delta

#reset the elements in the list from 0 to 1 according to their numbers.
def rank(sample_list):
    diff = 1/len(sample_list)
    copy1 = sample_list.copy()
    copy2 = sample_list.copy()
    while(len(copy1)>0):
        max_index = copy1.index(max(copy1))
        copy2[max_index] = diff*len(copy1)
        copy1.remove(copy1[max_index])
    return copy2


def weight_adjusting(sample_list, trader):
    last_price = [0]*len(tickers)
    for i in range(len(tickers)):
        bp = trader.getBestPrice(tickers[i])
        last_price[i] = bp.getLastPrice(tickers[i])
    last_price = rank(last_price).copy()
    total = sum(sample_list)
    weight = [i/total for i in sample_list]
    for i in range(len(tickers)):
        weight[i] = weight[i]*(last_price[i]) #use the price to measure the cap then use the cap to modify the weight
    return weight


delta_bid = check_signal_bid(Trader,tickers,2)
delta_ask = check_signal_ask(Trader,tickers,2)
weight_bid = weight_adjusting(delta_bid)
weight_ask = weight_adjusting(delta_ask)


def new_submit_buy(faker, weight_list , limit):
    money = [0]*len(tickers)
    buy_orders = [0]*len(tickers)
    for i in len(range(money)):
        money[i] = weight_list[i]*limit
        bp = faker.getBestPrice(tickers[i])
        order_price = bp.getBidPrice()
        buy_orders[i] = np.floor(money[i]/order_price)
        if money[i]!=0:
            Marketbuy = shift.Order(shift.Order.MARKET_BUY, tickers[i], buy_orders[i]/100)
            faker.submitOrder(Marketbuy)

#if each time we check something weird about the ask size
#we clean the position with the specified stock if the current position is greater than zero
#if the current position is not greater than zero, we check whether our buying power is enough for doing the short position.
def new_submit_sell(faker, weight_list,limit):
    index = [j for j in range(len(tickers)) if weight_list[j]!=0]
    money = [0]*len(tickers)
    for i in len(range(money)):
        money[i] = weight_list[i]*limit
        bp = faker.getBestPrice(tickers[i])
        order_price = bp.getAskSize()
    for i in index:
        item = faker.getPortfolioItem(tickers[i])
        current_position = item.getShares()
        if current_position > 0:
            Marketsell = shift.Order(shift.Order.MARKET_SELL,tickers[i],current_position/100)
            faker.submitOrder(Marketsell)
# if current_position < 0:
#     buying_power = faker.getPortfolioSummary().getTotalBp() #check the current buying power
#     if money[i]>buying_power:
#         sell_orders = np.floor(buying_power/order_price)
#     elif money[i]<= buying_power:
#         sell_orders = np.floor(money[i]/order_price)
#     Marketsell = shift.Order(shift.Order.MARKET_SELL,tickers[i],sell_orders)
#     faker.submitOrder(Marketsell)

