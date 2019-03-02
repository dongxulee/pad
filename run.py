import sys
sys.path.insert(0, 'include')
import shift
import time
from credentials import my_username, my_password
from stockAndPortfolio import Stock
import datetime


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
        stockList[ticker].dataAdd(info)

    '''
    ****************************************************************************
    Angli's Algorithm
    Only two major parameters are allowed here, for example:
    >> from liangRun.py import algorithm
    >> if i%10*60 == 0:
	>>     algorithm(trader, stockList)
    '''


    '''
    ****************************************************************************
    Weiping's Algorithm
    Only two major parameters are allowed here, for example:
    >> from liangRun.py import algorithm
    >> if i%10*60 == 0:
	>>     algorithm(trader, stockList)
    '''

    '''
    ****************************************************************************
    Dongxu's Algorithm
    Only two major parameters are allowed here, for example:
    >> from liangRun.py import algorithm
    >> if i%10*60 == 0:
	>>     algorithm(trader, stockList)
    '''

    '''
    ****************************************************************************
    Portfolio summary every minute
    '''
    # this is the test function for information collection
    if i % 60 == 0:
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

        # Time to stop the simulation.
        # if trader.getLastTradeTime().time() > datetime.time(15, 50):
        #     break
'''
********************************************************************************
End simulation clear all stocks in the portfolio book, and cancel all pending 
orders
'''

# clear all the portfolio items with market sell
for item in trader.getPortfolioItems().values():
    if item.getShares() > 0:
        endSell = shift.Order(shift.Order.MARKET_SELL, item.getSymbol(), item.getShares())
    else:
        endSell = shift.Order(shift.Order.MARKET_BUY, item.getSymbol(), -item.getShares())
    trader.submitOrder(endSell)

# cancel all pending orders
if trader.getWaitingListSize() != 0:
    if verbose:
        print("Canceling Pending Orders!")
    # trader.cancelAllPendingOrders()
    for order in trader.getWaitingList():
        trader.submitCancellation(order)
    while trader.getWaitingListSize() > 0:
        time.sleep(1)

























