import sys
sys.path.insert(0, 'include')
import shift
import time
from credentials import my_username, my_password
from stockAndPortfolio import Stock
import datetime
import numpy as np
import threading

from liangRun import efficient_frontier
from weipingRun import Weiping_Algorithm
from dongxuRun import neuralRegresion

'''
********************************************************************************
Initial parameter settings
'''

# Setup trader for accumulating information
verbose = 1
trader = shift.Trader(my_username)

# connect to the server
try:
    trader.connect("initiator.cfg", my_password)
except shift.IncorrectPassword as e:
    print(e)
    sys.exit(2)
except shift.ConnectionTimeout as e:
    print(e)
    sys.exit(2)

# subscribe to all available order books
trader.subAllOrderBook()

# simulation time
simulation_duration = 380

# companies in Dow
tickers = trader.getStockList()


# info diction for every ticker, can
stockList = dict()
for ticker in tickers:
    stockList[ticker] = Stock(ticker)

'''
multi-threading agents
'''
# class liangThread(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#     def run(self):
#         for i in range(1, simulation_duration * 60):
#             time.sleep(1)
#             if i%(60*60)==0:
#                 efficient_frontier(tickers, trader, stockList)
#             if i > 380 * 60:
#                 return
# liang = liangThread()

class weipingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        for i in range(1, simulation_duration * 60):
            time.sleep(1)
            if i%30==0 and i > 300:
                Weiping_Algorithm(trader, stockList, tickers)
            if i > 380 * 60:
                break
        return
weiping = weipingThread()
'''
********************************************************************************
Simulation Start
'''
weiping.start()
for i in range(1, simulation_duration*60):
    time.sleep(1)
    '''
    ****************************************************************************
    Data collection
    
    Example usage:
    To get the historical data for JPM, trace back to 10 seconds or 20 seconds:
    
    >> stockList['JPM'].historicalData(10)
    >> stockList['JPM'].historicalData(20)
    
    Default tracing back time is 10 seconds.
    '''
    if i%10 == 0:
        #information will be collected every second.
        for ticker in tickers:
            # info denotes the new information every second.
            # info list include:
            # ['bidPrice', 'bidSize', 'askPrice', 'askSize', 'lastPrice']
            info = []
            bp = trader.getBestPrice(ticker)
            info.append(bp.getBidPrice())
            info.append(bp.getAskSize())
            info.append(bp.getAskPrice())
            info.append(bp.getAskSize())
            info.append(trader.getLastPrice(ticker))
            orderBookPrice = []
            orderBookSize = []
            for order in trader.getOrderBook(ticker, shift.OrderBookType.GLOBAL_BID, maxLevel=10):
                orderBookPrice.append(order.price)
                orderBookSize.append(order.size)
            for order in trader.getOrderBook(ticker, shift.OrderBookType.GLOBAL_ASK, maxLevel=10):
                orderBookPrice.append(order.price)
                orderBookSize.append(order.size)
            info.append(np.array(orderBookSize))
            info.append(np.array(orderBookPrice))
            stockList[ticker].dataAdd(info)

    '''
    ****************************************************************************
    Angli's Algorithm
    Only three major parameters are allowed here, for example:
    >> from liangRun.py import algorithm
    >> if i%(10*60) == 0:
	>>     algorithm(tickers, trader, stockList)
    '''




    '''
    ****************************************************************************
    Weiping's Algorithm
    Only three major parameters are allowed here, for example:
    >> from liangRun.py import algorithm
    >> if i%(10*60) == 0:
	>>     algorithm(tickers, trader, stockList)
    '''
    # if i > 500 and i%10 == 0:
    #     Weiping_Algorithm(trader, stockList, tickers)





    '''
    ****************************************************************************
    Dongxu's Algorithm
    Only three major parameters are allowed here, for example:
    >> from liangRun.py import algorithm
    >> if i%(10*60) == 0:
	>>     algorithm(tickers, trader, stockList)
    '''
    # if i%(2*60) == 0:
    #     neuralRegresion(tickers, trader, stockList)




    '''
    ****************************************************************************
    Portfolio summary every minute
    '''
    # this is the test function for information collection
    if i % 20 == 0:
        if verbose:
            print()
            print(f"Trading Time: {i // 60} min")

        portfolioSummary = trader.getPortfolioSummary()
        # This method returns the total buying power available in the account.
        print("total buying power: {}".format(portfolioSummary.getTotalBP()))
        # This method returns the total amount of (long and short) shares
        # traded so far by the account.
        print("total share traded so far: {}".format(portfolioSummary.getTotalShares()))
        # This method returns the total realized P&L of the account.
        print("total P&L of the account {}".format(portfolioSummary.getTotalRealizedPL()))
        # Show all the items in portfolio
        print("portfolio summary: \n")
        print("Symbol\t\tShares\t\tPrice\t\tP&L\t\tTimestamp")
        for item in trader.getPortfolioItems().values():
            print("%6s\t\t%6d\t%9.2f\t%7.2f\t\t%26s" %
                  (item.getSymbol(), item.getShares(), item.getPrice(),
                   item.getRealizedPL(), item.getTimestamp()))

    # Time to stop the simulation.
    # if trader.getLastTradeTime().time() > datetime.time(15, 50):
    #         break
'''
********************************************************************************
End simulation clear all stocks in the portfolio book, and cancel all pending 
orders
'''

# cancel all pending orders
if trader.getWaitingListSize() != 0:
    if verbose:
        print("Canceling Pending Orders!")
    # trader.cancelAllPendingOrders()
    for order in trader.getWaitingList():
        trader.submitCancellation(order)
    while trader.getWaitingListSize() > 0:
        time.sleep(1)

# clear all the portfolio items with market sell
for item in trader.getPortfolioItems().values():
    if item.getShares() > 0:
        endSell = shift.Order(shift.Order.MARKET_SELL, item.getSymbol(), int(item.getShares()//100))
        trader.submitOrder(endSell)
    elif item.getShares() < 0:
        endSell = shift.Order(shift.Order.MARKET_BUY, item.getSymbol(), int(-item.getShares()//100))
        trader.submitOrder(endSell)
print("Clear portfolio! \n")



time.sleep(10*60)
print("portfolio summary-----------------------------------------------------")
portfolioSummary = trader.getPortfolioSummary()
# This method returns the total buying power available in the account.
print("total buying power: {}".format(portfolioSummary.getTotalBP()))
# This method returns the total amount of (long and short) shares
# traded so far by the account.
print("total share traded so far: {}".format(portfolioSummary.getTotalShares()))
# This method returns the total realized P&L of the account.
print("total P&L of the account {}".format(portfolioSummary.getTotalRealizedPL()))


print("portfolio summary: \n")
print("Symbol\t\tShares\t\tPrice\t\tP&L\t\tTimestamp")
for item in trader.getPortfolioItems().values():
    print("%6s\t\t%6d\t%9.2f\t%7.2f\t\t%26s" %
          (item.getSymbol(), item.getShares(), item.getPrice(),
           item.getRealizedPL(), item.getTimestamp()))



















