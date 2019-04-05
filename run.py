import sys
import shift
import time
from credentials import my_username, my_password
from stockAndPortfolio import Stock, portfolioInfo, infoCollecting, clearAllPortfolioItems, cancelAllPendingOrders
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
timeToStop = datetime.time(15, 50)
# All companies' ticker in Dow Jones
tickers = trader.getStockList()
# info diction for every ticker
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
    Data collection in every second
    '''
    if i % 1 == 0:
        # information will be collected every second.
        infoCollecting(trader, tickers, stockList, length = 500)
    '''
    ****************************************************************************
    Portfolio summary every 10 seconds
    '''
    # this is the test function for information collection
    if i % 10 == 0 and verbose:
        print("\n")
        print(f"Trading Time: {i // 60} min")
        print(trader.getLastTradeTime().time())
        portfolioInfo(trader)
    '''
    ****************************************************************************
    Dongxu's strategy
    '''
    dongxuStartTime = 360
    dongxuTimeInterval = 1
    if i > dongxuStartTime and i % dongxuTimeInterval == 0:
        marketMaker(2, trader, stockList, tickers, lookBack = 305,
                                    lag = 3,
                                    numNeighbors = 10, decay = 1)


    '''
    ****************************************************************************
    Risk Control and time management 
    '''
    # substantial loss happen terminate the program
    if i % 60 == 0:
        portfolioSummary = trader.getPortfolioSummary()
        if portfolioSummary.getTotalRealizedPL() < -1000.00 \
                or portfolioSummary.getTotalBP() < 600000:
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
clearAllPortfolioItems(trader, tickers)
time.sleep(200)
# Print out the portfolio summary
print("portfolio summary-----------------------------------------------------")
portfolioInfo(trader)

trader.disconnect()
