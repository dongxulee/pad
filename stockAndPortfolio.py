import pandas as pd
import shift
import numpy as np
import time

# This is just for now
columnsNames = ['bidPrice', 'bidSize', 'askPrice', 'askSize', 'lastPrice', 'orderBook']

class Stock:
    def __init__(self, name):
        self.name = name
        self.histData = pd.DataFrame(columns=columnsNames)

    def dataAdd(self, info):
        df = pd.DataFrame([info], columns=columnsNames)
        self.histData = self.histData.append(df, ignore_index=True)

    def showData(self, num=5):
        print(self.histData.tail(num))
        
    def historicalData(self, num=10):
        return self.histData.tail(num)

    def getData(self):
        return self.histData

    def refreshData(self):
        self.histData = self.histData.tail(300)



def portfolioInfo(trader):
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


def infoCollecting(trader, tickers, stockList):
    for ticker in tickers:
        # info denotes the new information every second.
        # info list include:
        # ['bidPrice', 'bidSize', 'askPrice', 'askSize', 'lastPrice', 'orderBook']
        info = []
        bp = trader.getBestPrice(ticker)
        info.append(bp.getBidPrice())
        info.append(bp.getAskSize())
        info.append(bp.getAskPrice())
        info.append(bp.getAskSize())
        info.append(trader.getLastPrice(ticker))
        size = []
        for order in trader.getOrderBook(ticker, shift.OrderBookType.GLOBAL_BID, 10):
            size.append(order.size)
        size = [0]*(10-len(size)) + size
        for order in trader.getOrderBook(ticker, shift.OrderBookType.GLOBAL_ASK, 10):
            size.append(order.size)
        size = size + [0]*(20 - len(size))
        info.append(np.array(size))
        stockList[ticker].dataAdd(info)


def cancelAllPendingOrders(trader):
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
        print("Order Canceled!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

def clearAllPortfolioItems(trader):
    # clear all the portfolio items with market sell
    for item in trader.getPortfolioItems().values():
        if item.getShares() > 0:
            endSell = shift.Order(shift.Order.MARKET_SELL, item.getSymbol(), int(item.getShares()/100))
            trader.submitOrder(endSell)
        elif item.getShares() < 0:
            endSell = shift.Order(shift.Order.MARKET_BUY, item.getSymbol(), int(item.getShares()/100))
            trader.submitOrder(endSell)
    time.sleep(5)
    print("Clear portfolio!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
