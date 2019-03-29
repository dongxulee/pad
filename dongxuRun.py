import shift
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import time

def setupBuyOrder(trader, ticker, signal):
    bp = trader.getBestPrice(ticker)
    eps = 0.01 * (bp.getAskPrice() - bp.getBidPrice())
    limit_buy = shift.Order(shift.Order.LIMIT_BUY, ticker, 1,
                            bp.getBidPrice() + eps * signal)
    trader.submitOrder(limit_buy)

def setupSellOrder(trader, ticker, signal):
    bp = trader.getBestPrice(ticker)
    eps = 0.01 * (bp.getAskPrice() - bp.getBidPrice())
    limit_sell = shift.Order(shift.Order.LIMIT_SELL, ticker, 1,
                             bp.getAskPrice() + eps * signal)
    trader.submitOrder(limit_sell)



def upDateOrder(trader, signal, ticker):
    # Get the waiting list to see the current order for this particular ticker
    Order = [order for order in trader.getWaitingList() if order.symbol == ticker]
    # If there is no order for this ticker, there are two possibilities
    if len(Order) == 0:
        # Order got executed and there is share in the portfolio
        item = trader.getPortfolioItem(ticker)
        if item.getShares() != 0:
            if item.getShares() > 0 and signal <= 0:
                setupSellOrder(trader, ticker, signal)
            elif item.getShares() < 0 and signal >= 0:
                setupBuyOrder(trader, ticker, signal)
        else:
            # No order gets executed, so setup the initial buy and sell
            if signal > 0:
                setupBuyOrder(trader, ticker, signal)

            elif signal < 0:
                 setupSellOrder(trader, ticker, signal)

    # If there is a sell or buy order pending, check the signal.
    elif len(Order) == 1:
        if signal > 0:
            for order in Order:
                if order.type == shift.Order.LIMIT_BUY:
                    trader.submitCancellation(order)
                    setupBuyOrder(trader, ticker, signal)
                else:
                    trader.submitCancellation(order)
        elif signal < 0:
            for order in Order:
                if order.type == shift.Order.LIMIT_BUY:
                    trader.submitCancellation(order)
                else:
                    trader.submitCancellation(order)
                    setupSellOrder(trader, ticker, signal)
        else:
            for order in Order:
                trader.submitCancellation(order)
    else:
        # write this part just as protection
        item = trader.getPortfolioItem(ticker)
        if item.getShares() != 0:
            if item.getShares() > 0 and signal <= 0:
                setupSellOrder(trader, ticker, signal)
            elif item.getShares() < 0 and signal >= 0:
                setupBuyOrder(trader, ticker, signal)
        time.sleep(1)
        for order in Order:
            trader.submitCancellation(order)


# could modify this function as multi-threading market makers
def marketMaker(maker, trader, stockList, tickers, lookBack, lag,
                                 numNeighbors, decay):
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    for ticker in tickers:
        if maker == 1:
            signal = signalGenerator1(stockList, ticker = ticker,
                                     lookBack = lookBack, lag = lag,
                                     numNeighbors = numNeighbors, decay = decay)
        elif maker == 2:
            signal = signalGenerator2(stockList, ticker = ticker,
                                     lookBack = lookBack, lag = lag,
                                     decay = decay)
        else:
            signal = 0
        upDateOrder(trader, signal, ticker = ticker)




def signalGenerator1(stockList, ticker, lookBack , lag, numNeighbors, decay):
    '''
     k nearest neighbor classifier.
     input: stockList
     output: signalGenerator output {-1, 0, 1} signals, setup a threshold delta.

     delta could be something related to volatility
    '''
    # data preparation part
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
    # training and prediction part
    generator = KNeighborsClassifier(numNeighbors)
    generator.fit(np.array(xTrain), np.array(yTrain))
    return generator.predict([X])[0]



def signalGenerator2(stockList, ticker, lookBack , lag, decay):
    '''
     SVM with rbf kernel classifier.
     input: stockList
     output: signalGenerator output {-1, 0, 1} signals, setup a threshold delta.

     delta could be something related to volatility
    '''
    # data preparation part
    data = stockList[ticker].historicalData(lookBack)
    data = data.reset_index(drop=True)
    X = data["orderBook"][lookBack-1]
    xTrain = []
    yTrain = []
    delta = data["lastPrice"].std() * (lag**(1/2)) * decay
    for i in range(0, lookBack - lag):
        xTrain.append(data["orderBook"][i])
        jump = data["lastPrice"][i + lag] - data["lastPrice"][i]
        if jump > delta or jump > 0.3:
            yTrain.append(1)
        elif jump < -delta or jump < -0.3:
            yTrain.append(-1)
        else:
            yTrain.append(0)
    # training and prediction part
    if len(set(yTrain)) != 1:
        generator = SVC(gamma='auto')
        generator.fit(np.array(xTrain), np.array(yTrain))
        return generator.predict([X])[0]
    else:
        return 0