import shift
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
import time


def setupBuyOrder(trader, ticker, signal):
    bp = trader.getBestPrice(ticker)
    limit_buy = shift.Order(shift.Order.LIMIT_BUY, ticker, 1,
                            bp.getBidPrice() + 0.01 * signal)
    trader.submitOrder(limit_buy)

def setupSellOrder(trader, ticker, signal):
    bp = trader.getBestPrice(ticker)
    limit_sell = shift.Order(shift.Order.LIMIT_SELL, ticker, 1,
                             bp.getAskPrice() + 0.01 * signal)
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

    # patch
    item = trader.getPortfolioItem(ticker)
    if item.getShares() >= 300:
        closeOrder = shift.Order(shift.Order.MARKET_SELL, ticker, int(item.getShares() / 100))
        trader.submitOrder(closeOrder)

    elif item.getShares() <= -300:
        closeOrder = shift.Order(shift.Order.MARKET_BUY, ticker, int(-item.getShares() / 100))
        trader.submitOrder(closeOrder)




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
        # elif maker == 3:
        #     signal = signalGenerator3(stockList, modelList, ticker=ticker,
        #                               lookBack=lookBack, lag=lag,
        #                               )

        else:
            signal = 0
        print(signal, end = "**")
        upDateOrder(trader, signal, ticker = ticker)




def signalGenerator1(stockList, ticker, lookBack , lag, numNeighbors, decay):
    '''
     k nearest neighbor classifier.
     input: stockList
     output: signalGenerator output {-1, 0, 1} signals, setup a threshold delta.

     delta could be something related to volatility
    '''
    pro = 0.05
    # data preparation part
    data = stockList[ticker].historicalData(lookBack)
    data = data.reset_index(drop=True)
    X = data["orderBook"][lookBack - 1]
    xTrain = []
    yTrain = []
    delta_low = data["lastPrice"].pct_change(lag).quantile(pro)
    delta_high = data["lastPrice"].pct_change(lag).quantile(1-pro)
    for i in range(0, lookBack - lag):
        xTrain.append(data["orderBook"][i])
        if data["lastPrice"][i] != 0:
            jump = (data["lastPrice"][i + lag] - data["lastPrice"][i]) / data["lastPrice"][i]
        else:
            jump = 0
        if jump > delta_high:
            yTrain.append(1)
        elif jump < delta_low:
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

    pro = 0.025
    # data preparation part
    data = stockList[ticker].historicalData(lookBack)
    data = data.reset_index(drop=True)
    X = data["orderBook"][lookBack-1]
    xTrain = []
    yTrain = []
    delta_low = -0.0005 #data["lastPrice"].pct_change(lag).quantile(pro)
    delta_high = 0.0005 #data["lastPrice"].pct_change(lag).quantile(1-pro)
    for i in range(0, lookBack - lag):
        xTrain.append(data["orderBook"][i])
        if data["lastPrice"][i] != 0:
            jump = (data["lastPrice"][i + lag] - data["lastPrice"][i])/data["lastPrice"][i]
        else:
            jump = 0

        if jump > delta_low and jump < delta_high:
            yTrain.append(0)
        elif jump > 2*delta_low and jump < delta_low:
            yTrain.append(-1)
        elif jump > delta_high and jump < 2*delta_high:
            yTrain.append(1)
        elif jump < 2*delta_low and jump > 3*delta_low:
            yTrain.append(-2)
        elif jump > 2*delta_high and jump < 3*delta_high:
            yTrain.append(2)
        elif jump < 3*delta_low and jump > 4*delta_low:
            yTrain.append(-3)
        elif jump > 3*delta_high and jump < 4*delta_high:
            yTrain.append(3)
        elif jump < 4*delta_low and jump > 5*delta_low:
            yTrain.append(-4)
        elif jump > 4*delta_high and jump < 5*delta_high:
            yTrain.append(4)
        elif jump < 5 * delta_low and jump > 6 * delta_low:
            yTrain.append(-5)
        elif jump > 5 * delta_high and jump < 6 * delta_high:
            yTrain.append(5)
        elif jump < 6 * delta_low and jump > 7 * delta_low:
            yTrain.append(-6)
        elif jump > 6 * delta_high and jump < 7 * delta_high:
            yTrain.append(6)
        elif jump < 7 * delta_low and jump > 8 * delta_low:
            yTrain.append(-10)
        elif jump > 7 * delta_high and jump < 8 * delta_high:
            yTrain.append(10)
        elif jump < 8 * delta_low and jump > 9 * delta_low:
            yTrain.append(-15)
        elif jump > 8 * delta_high and jump < 9 * delta_high:
            yTrain.append(15)
        elif jump < 9 * delta_low and jump > 10 * delta_low:
            yTrain.append(-20)
        elif jump > 9 * delta_high and jump < 10 * delta_high:
            yTrain.append(20)
        elif jump < 10 * delta_low and jump > 11 * delta_low:
            yTrain.append(-25)
        elif jump > 10 * delta_high and jump < 11 * delta_high:
            yTrain.append(25)
        elif jump < 11 * delta_low:
            yTrain.append(-30)
        elif jump > 11 * delta_high:
            yTrain.append(30)
        else:
            yTrain.append(0)

    # training and prediction part
    if len(set(yTrain)) != 1:
        generator = SVC(gamma='auto', kernel='rbf', class_weight="balanced")
        generator.fit(np.array(xTrain), np.array(yTrain))
        return generator.predict([X])[0]
    else:
        return 0



def signalGenerator3(stockList, modelList, ticker, lookBack , lag):
    '''
     Neural network classifier.
     input: stockList
     output: signalGenerator output {-1, 0, 1} signals, setup a threshold delta.

     delta could be something related to volatility
    '''

    pro = 0.025
    split = 200
    # data preparation part
    data = stockList[ticker].historicalData(lookBack)
    data = data.reset_index(drop=True)
    X = data["orderBook"][lookBack-1]
    xTrain = []
    yTrain = []
    delta_low = -0.0005 #data["lastPrice"].pct_change(lag).quantile(pro)
    delta_high = 0.0005 #data["lastPrice"].pct_change(lag).quantile(1-pro)
    for i in range(0, lookBack - lag):
        xTrain.append(data["orderBook"][i])
        if data["lastPrice"][i] != 0:
            jump = (data["lastPrice"][i + lag] - data["lastPrice"][i])/data["lastPrice"][i]
        else:
            jump = 0
        if jump > delta_high:
            yTrain.append([1, 0, 0])
        elif jump < delta_low:
            yTrain.append([0, 1, 0])
        else:
            yTrain.append([0, 0, 1])

    # training and prediction part
    generator = modelList[ticker]
    generator.train_on_batch(np.array(xTrain[:split]), np.array(yTrain[:split]))
    test_loss, test_acc = generator.evaluate(np.array(xTrain[split:]), np.array(yTrain[split:]))
    print(test_acc)
    if test_acc >= 0.80:
        prediction = generator.predict(np.array([X]))[0]
        if np.argmax(prediction) == 0:
            return 1
        elif np.argmax(prediction) == 1:
            return -1
        else:
            return 0
    else:
        return 0