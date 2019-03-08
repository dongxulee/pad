import sys
sys.path.insert(0, 'include')
import shift
import time
from credentials import my_username, my_password
from stockAndPortfolio import Stock, portfolioSummary, infoCollecting
import datetime
import threading

from liangRun import efficient_frontier
from weipingRun import Weiping_Algorithm
from dongxuRun import marketMaker

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
# Time to stop the simulation
timeToStop = datetime.time(15, 30)
# All companies' ticker in Dow Jones
tickers = trader.getStockList()
# info diction for every ticker
stockList = dict()
for ticker in tickers:
    stockList[ticker] = Stock(ticker)




'''
********************************************************************************
multi-threading agents, define the algorithm running time below
'''
weipingStartTime = 300
weipingTimeInterval = 30
class weipingThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        for i in range(1, simulation_duration * 60):
            time.sleep(1)
            if i%weipingTimeInterval==0 and i > weipingStartTime:
                Weiping_Algorithm(trader, stockList, tickers)
            if trader.getLastTradeTime().time() > timeToStop:
                return
#
#
# liangStartTime = 1600
# liangTimeInterval = 60*30
# class weipingThread(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#     def run(self):
#         for i in range(1, simulation_duration * 60):
#             time.sleep(1)
#             if i%liangTimeInterval==0 and i > liangStartTime:
#                 efficient_frontier(tickers, trader, stockList)
#             if trader.getLastTradeTime().time() > timeToStop:
#                 return


# dongxuStartTime = 1000
# dongxuTimeInterval = 0.01
# class dongxuThread(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#     def run(self):
#         for i in range(1, simulation_duration * 60 * 100):
#             time.sleep(dongxuTimeInterval)
#             if i > dongxuStartTime:
#                 marketMaker(tickers, trader, i)
#             if trader.getLastTradeTime().time() > timeToStop:
#                 return

# dongxu = dongxuThread()
weiping = weipingThread()
# liang = weipingThread()
weiping.start()
# # liang.start()
# dongxu.start()


'''
********************************************************************************
Simulation Start
'''
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
        #information will be collected every 10 second.
        infoCollecting(trader, tickers, stockList)
    '''
    ****************************************************************************
    Portfolio summary every 20 seconds
    '''
    # this is the test function for information collection
    if i % 10 == 0:
        if verbose:
            print()
            print(f"Trading Time: {i // 60} min")

        portfolioSummary(trader)

    # Time to stop the simulation.
    if trader.getLastTradeTime().time() > timeToStop:
            break




'''
********************************************************************************
End simulation clear all stocks in the portfolio book, and cancel all pending 
orders
'''

# cancel all pending orders
if trader.getWaitingListSize() != 0:
    # print("Canceling Pending Orders!")
    for order in trader.getWaitingList():
        if order.type == shift.Order.LIMIT_BUY:
            order.type = shift.Order.CANCEL_BID
        else:
            order.type = shift.Order.CANCEL_ASK
        trader.submitOrder(order)
        while (trader.getWaitingListSize() != 0):
            time.sleep(0.1)
        print("Order Canceled!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


# clear all the portfolio items with market sell
for item in trader.getPortfolioItems().values():
    if item.getShares() > 0:
        endSell = shift.Order(shift.Order.MARKET_SELL, item.getSymbol(), int(item.getShares()//100))
        trader.submitOrder(endSell)
    elif item.getShares() < 0:
        endSell = shift.Order(shift.Order.MARKET_BUY, item.getSymbol(), int(-item.getShares()//100))
        trader.submitOrder(endSell)
print("Clear portfolio! \n")


# Wait several minutes for the market order to get executed
time.sleep(7*60)
print("portfolio summary-----------------------------------------------------")
portfolioSummary(trader)

trader.disconnect()



















