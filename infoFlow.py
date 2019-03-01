import sys
sys.path.insert(0, 'include')
import shift
import time
from stockAndPortfolio import Stock, Portfolio

# Setup trader for accumulating information
client_id_number = 6  # client ID number
verbose = 1
client_id = f"test{str(client_id_number).zfill(3)}"
trader = shift.Trader(client_id)

# connect to the server
try:
    trader.connect("initiator.cfg", "password")
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


# # info diction for every ticker, can
# infoList = dict()
# for ticker in tickers:
#     infoList[ticker] = Stock(ticker)

for i in range(1, simulation_duration):
    time.sleep(5)
    print(i)
    if verbose:
        print()
        print(f"Trading Time: {i}")
    for ticker in tickers:
        bp = trader.getBestPrice(ticker)
        print("Get the best bid price: \n")
        print(bp.getBidPrice())
        print("Get the best bid size: \n")
        print(bp.getBidSize())
        print("Get the best ask price: \n")
        print(bp.getAskPrice())
        print("Get the best ask size: \n")
        print(bp.getAskSize())