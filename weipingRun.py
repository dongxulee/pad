import numpy as np
import shift
from sklearn.neighbors import KernelDensity

# def rank(sample_list):
#     diff = 1 / len(sample_list)
#     copy1 = sample_list.copy()
#     copy2 = sample_list.copy()
#     while (len(copy1) > 0):
#         max_index = copy1.index(max(copy1))
#         copy2[max_index] = diff * len(copy1)
#         copy1.remove(copy1[max_index])
#     return copy2

def rank(sample_list):
    index = 1
    for i in np.argsort(sample_list):
        sample_list[i] = index / len(sample_list)
        index = index + 1
    return sample_list

# stockList['AAPL'].tail(500) => pandas dataFrame, shape: 500*5
# pandas
def Weiping_Algorithm(trader, stockList, tickers):
    delta_bid = []
    delta_ask = []
    for stock in tickers:
        bp = trader.getBestPrice(stock)
        step = 0.01
        check_bidsize = bp.getBidSize()
        sim_bid = np.arange(0, check_bidsize, step)
        check_asksize = bp.getAskSize()
        sim_ask = np.arange(0, check_asksize, step)
        lookback = 200
        
        # get the last 500 history size data to fit the distribution of the moving window
        history_bidsize = stockList[stock].historicalData(lookback).bidSize
        history_asksize = stockList[stock].historicalData(lookback).askSize
        history_bidsize = np.array(history_bidsize)
        history_asksize = np.array(history_asksize)
        kde_bid = KernelDensity(bandwidth=1.0, kernel="gaussian").fit(history_bidsize[:, None])
        kde_ask = KernelDensity(bandwidth=1.0, kernel="gaussian").fit(history_asksize[:, None])
        # check_bidsize = np.array([check_bidsize])
        # check_asksize = np.array([check_asksize])
        # log_den_bid = kde_bid.score_sample(check_bidsize[:,None])
        # log_den_ask = kde_ask.score_sample(check_asksize[:,None])
        # d_prob_bid = np.exp(log_den_bid)
        # d_prob_ask = np.exp(log_den_ask)
        prob_bid = 0.0
        prob_ask = 0.0
        for k in sim_bid:
            temp_bid = np.array([k])
            prob_bid = prob_bid + (np.exp(kde_bid.score_samples(temp_bid[:, None]))) * step
        for k in sim_ask:
            temp_ask = np.array([k])
            prob_ask = prob_ask + (np.exp(kde_ask.score_samples(temp_ask[:, None]))) * step
        pvalue_bid = 1 - prob_bid
        pvalue_ask = 1 - prob_ask
        thresold_bid = 0.2
        thresold_ask = 0.2
        new_bid = 0.0
        new_ask = 0.0
        # check the unusual size
        if pvalue_bid < thresold_bid:
            new_bid = 1 / pvalue_bid
        if prob_ask < thresold_ask:
            new_ask = 1 / pvalue_ask
        if new_bid:
            delta_bid.append(new_bid)
        else:
            delta_bid.append(0)
        if new_ask:
            delta_ask.append(new_ask)
        else:
            delta_ask.append(0)

# weight adjusting
    last_price = [0] * len(tickers)
    for k in range(len(tickers)):
        last_price[k] = trader.getLastPrice(tickers[k])
    last_price = rank(last_price).copy()
    total_bid = sum(delta_bid)
    total_ask = sum(delta_ask)
    if total_bid != 0:
        weight_bid = [delta / total_bid for delta in delta_bid]
    elif total_bid==0:
        weight_bid = [0]*len(delta_bid)
    if total_ask != 0:
        weight_ask = [delta / total_ask for delta in delta_ask]
    elif total_ask==0:
        weight_ask = [0]*len(delta_ask)
    for stock in range(len(tickers)):
        weight_bid[stock] = weight_bid[stock] * last_price[stock]
        weight_ask[stock] = weight_ask[stock] * last_price[stock]

#order submit
    limit = 50000
    money_long = [0] * len(tickers)
    money_short = [0] * len(tickers)
    for k in range(len(money_long)):
        buying_power = trader.getPortfolioSummary().getTotalBP()
        if buying_power < limit:
            limit = buying_power
        money_long[k] = limit * weight_bid[k]
        money_short[k] = limit * weight_ask[k]
        bp = trader.getBestPrice(tickers[k])
        buy_orders_price = bp.getBidPrice()
        sell_orders_price = bp.getAskPrice()
        # submit buy orders
        if money_long[k] != 0:
            buy_orders = np.floor(money_long[k] / buy_orders_price)
            if (buy_orders / 100) >= 1:
                Makrketbuy = shift.Order(shift.Order.MARKET_BUY, tickers[k], int(buy_orders // 100))
                trader.submitOrder(Makrketbuy)
            else:
                if (buy_orders / 100) > 0.5:
                    Makrketbuy = shift.Order(shift.Order.MARKET_SELL, tickers[k], 1)
                    trader.submitOrder(Makrketbuy)
        # submit sell orders
        if money_short[k] != 0:
            item = trader.getPortfolioItem(tickers[k])
            current_postion = item.getShares()
            if current_postion > 0:
                sell_orders = current_postion * weight_ask[k]
                if (sell_orders / 100) >= 1:
                    Marketsell = shift.Order(shift.Order.MARKET_SELL, tickers[k], int(sell_orders // 100))
                    trader.submitOrder(Marketsell)
                else:
                    if (sell_orders / 100) > 0.5:
                        Marketsell = shift.Order(shift.Order.MARKET_SELL, tickers[k], 1)
                        trader.submitOrder(Marketsell)
            if current_postion < 0:
                buying_power = trader.getPortfolioSummary().getTotalBP()
                if money_short[k] > buying_power:
                    sell_orders = np.floor(buying_power / sell_orders_price)
                    if money_short[k] <= buying_power:
                        sell_orders = np.floor(money_short[k] / sell_orders_price)
                    if (sell_orders / 100) >= 1:
                        Marketsell = shift.Order(shift.Order.MARKET_SELL, tickers[k], int(sell_orders // 100))
                        trader.submitOrder(Marketsell)
                    else:
                        if (sell_orders / 100) > 0.5:
                            Marketsell = shift.Order(shift.Order.MARKET_SELL, tickers[k], 1)
                            trader.submitOrder(Marketsell)
