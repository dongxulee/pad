import sys
sys.path.insert(0, 'include')
import shift
import time
from credentials import my_username, my_password
from stockAndPortfolio import Stock, portfolioInfo, infoCollecting, cancelAllPendingOrders, clearAllPortfolioItems
import datetime
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
    if i%1 == 0:
        #information will be collected every 10 second.
        infoCollecting(trader, tickers, stockList)

    if i % (20*60) == 0:
        for ticker in tickers:
            stockList[ticker].refreshData()
    '''
    ****************************************************************************
    Portfolio summary every 20 seconds
    '''
    # this is the test function for information collection
    if i % 20 == 0:
        if verbose:
            print("\n")
            print(f"Trading Time: {i // 60} min")
            print(trader.getLastTradeTime().time())

        portfolioInfo(trader)


    '''
    ****************************************************************************
    Dongxu's strategy
    '''
    dongxuStartTime = 60*4
    dongxuTimeInterval = 10
    if (i > dongxuStartTime) and i%dongxuTimeInterval == 0:
        marketMaker(trader, stockList, tickers, lookBack = 200,
                                    lag = 9,
                                    numNeighbors = 7, decay = 0.8)

    # substantial loss happen terminate the program
    if i%(60) == 0:
        portfolioSummary = trader.getPortfolioSummary()
        if portfolioSummary.getTotalRealizedPL() < -2000.00 \
                or portfolioSummary.getTotalBP() < 300000:
            break
        # Time to stop the simulation.
        if trader.getLastTradeTime().time() > timeToStop:
            break

'''
********************************************************************************
End simulation clear all stocks in the portfolio book, and cancel all pending 
orders
'''

# cancel all pending orders
cancelAllPendingOrders(trader)
# clear all the portfolio items with market sell
clearAllPortfolioItems(trader)


# Wait several minutes for the orders to get executed
time.sleep(7*60)
print("portfolio summary-----------------------------------------------------")
portfolioInfo(trader)

trader.disconnect()