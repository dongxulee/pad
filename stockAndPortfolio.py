import pandas as pd
import shift
import numpy as np
import time
from dongxuRun import setupSellOrder, setupBuyOrder

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

    def refreshData(self, num):
        self.histData = self.histData.tail(num)


def infoCollecting(trader, tickers, stockList, length):
    depth = 10
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
        for order in trader.getOrderBook(ticker, shift.OrderBookType.GLOBAL_BID, depth):
            size.append(order.size)
        size = [0]*(depth-len(size)) + size
        for order in trader.getOrderBook(ticker, shift.OrderBookType.GLOBAL_ASK, depth):
            size.append(order.size)
        size = size + [0]*(depth*2 - len(size))
        info.append(np.array(size))
        stockList[ticker].dataAdd(info)
        if stockList[ticker].getData().shape[0] > length:
            stockList[ticker].refreshData(int(length*0.8))



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



def clearAllPortfolioItems(trader, tickers):
    # clear all the portfolio items with market sell
    for ticker in tickers:
        item = trader.getPortfolioItem(ticker)
        if item.getShares() > 0:
            closeOrder = shift.Order(shift.Order.MARKET_SELL, ticker, item.getShares())
            trader.submitOrder(closeOrder)
        elif item.getShares() < 0:
            closeOrder = shift.Order(shift.Order.MARKET_BUY, ticker, -item.getShares())
            trader.submitOrder(closeOrder)
    time.sleep(60)
    print("Clear portfolio!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")


def cancelAllPendingOrders(trader):
    for order in trader.getWaitingList():
            trader.submitCancellation(order)