import numpy as np
from keras.layers import Dense
from keras.models import Sequential
import shift
import time

def neuralRegresion(tickers, trader, stockList):
    ############################################################################
    # clear all the portfolio items with market sell
    for item in trader.getPortfolioItems().values():
        if item.getShares() > 0:
            endSell = shift.Order(shift.Order.MARKET_SELL, item.getSymbol(),
                                  item.getShares())
        else:
            endSell = shift.Order(shift.Order.MARKET_BUY, item.getSymbol(),
                                  -item.getShares())
        trader.submitOrder(endSell)

    # cancel all pending orders
    if trader.getWaitingListSize() != 0:
        print("Canceling Pending Orders!")
        # trader.cancelAllPendingOrders()
        for order in trader.getWaitingList():
            trader.submitCancellation(order)
        while trader.getWaitingListSize() > 0:
            time.sleep(1)
    ############################################################################
    # model training part
    numData = 100
    model = Sequential()
    model.add(Dense(units=40, activation='softmax', input_dim=40))
    model.add(Dense(units=100, activation='relu'))
    model.add(Dense(units=10, activation='relu'))
    model.add(Dense(1, activation='relu'))
    model.compile(optimizer='adam', loss='mean_squared_error')
    X_train = []
    Y_train = []
    timeShift = 30
    for ticker in tickers:
        stockInfo = stockList[ticker].historicalData(numData)
        for i in range(numData - timeShift):
            X_train.append(stockInfo.orderBookPrice[i] * stockInfo.orderBookSize[i])
        for j in range(numData - timeShift):
            Y_train.append(stockInfo.lastPrice[j+timeShift])
    model.fit(np.array(X_train), np.array(Y_train), epochs=5, batch_size=32)


    # order execution part based on the model prediction
    for ticker in tickers:
        stockInfo = stockList[ticker].historicalData(2)
        X = stockInfo.orderBookPrice[-1] * stockInfo.orderBookSize[-1]
        predictPrice = model.predict(X)
        bp = trader.getBestPrice(ticker)
        if predictPrice > bp.getBidPrice():
            limit_buy = shift.Order(shift.Order.LIMIT_BUY, ticker, 10, bp.getAskPrice())
            trader.submitOrder(limit_buy)
        elif predictPrice < bp.getAskPrice():
            limit_sell = shift.Order(shift.Order.LIMIT_SELL, ticker, 10, bp.getBidPrice())
            trader.submitOrder(limit_sell)