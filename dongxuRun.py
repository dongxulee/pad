import shift
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import time

def signalGenerator(stockList, ticker, lookBack , lag, numNeighbors, decay = 0.2):
    '''
     k nearest neighbor classifier.
     input: stockList
     output: signalGenerator output {-1, 0, 1} signals, setup a threshold delta.

     delta could be something related to volatility
    '''

    data = stockList[ticker].historicalData(lookBack)
    data = data.reset_index(drop=True)
    X = data["orderBook"][lookBack-1]
    xTrain = []
    yTrain = []
    delta = data["lastPrice"].std() * (lag**(1/2)) * decay
    for i in range(0, lookBack - lag):
        xTrain.append(data["orderBook"][i])
        jump = data["lastPrice"][i + lag] - data["lastPrice"][i]
        if jump > delta or jump > 0.5:
            yTrain.append(1)
        elif jump < -delta or jump < -0.5:
            yTrain.append(-1)
        else:
            yTrain.append(0)
    generator = KNeighborsClassifier(numNeighbors)
    generator.fit(np.array(xTrain), np.array(yTrain))
    return generator.predict([X])[0]

def upDateOrder(trader, signal, ticker):
    # First cancel the original order
    Order = [order for order in trader.getWaitingList() if order.symbol == ticker]
    if len(Order) == 0 and signal != 0:
        bp = trader.getBestPrice(ticker)
        eps = 0.1 * (bp.getAskPrice() - bp.getBidPrice())
        limit_buy = shift.Order(shift.Order.LIMIT_BUY, ticker, 1,
                                bp.getBidPrice() + eps*signal)
        limit_sell = shift.Order(shift.Order.LIMIT_SELL, ticker, 1,
                                 bp.getAskPrice() + eps*signal)
        trader.submitOrder(limit_buy)
        trader.submitOrder(limit_sell)

    elif len(Order) == 1:
        for order in Order:
            if order.type == shift.Order.LIMIT_BUY:
                order.type = shift.Order.CANCEL_BID
                trader.submitOrder(order)
                bp = trader.getBestPrice(ticker)
                eps = 0.01 * (bp.getAskPrice() - bp.getBidPrice())
                limit_buy = shift.Order(shift.Order.LIMIT_BUY, ticker, 1,
                                        bp.getBidPrice() + eps)
                trader.submitOrder(limit_buy)
            else:
                order.type = shift.Order.CANCEL_ASK
                trader.submitOrder(order)
                bp = trader.getBestPrice(ticker)
                eps = 0.01 * (bp.getAskPrice() - bp.getBidPrice())
                limit_sell = shift.Order(shift.Order.LIMIT_SELL, ticker, 1,
                                         bp.getAskPrice() - eps)
                trader.submitOrder(limit_sell)

    else:
        for order in Order:
            if order.type == shift.Order.LIMIT_BUY:
                order.type = shift.Order.CANCEL_BID
                trader.submitOrder(order)
            else:
                order.type = shift.Order.CANCEL_ASK
                trader.submitOrder(order)




# could modify this function as multi-threading market makers
def marketMaker(trader, stockList, tickers, lookBack, lag,
                                 numNeighbors, decay):
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    for ticker in tickers:
        signal = signalGenerator(stockList, ticker = ticker,
                                 lookBack = lookBack, lag = lag,
                                 numNeighbors = numNeighbors, decay = decay)
        upDateOrder(trader, signal, ticker = ticker)