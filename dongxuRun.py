import shift
import time

def marketMaker(tickers, trader, i):
    for ticker in tickers:
        bp = trader.getBestPrice(ticker)
        bid = bp.getBidPrice()
        ask = bp.getAskPrice()
        spread = ask-bid
        if spread > 0.05:
            eps = 0.01
            limit_buy = shift.Order(shift.Order.LIMIT_BUY, ticker,1, bid+eps)
            limit_sell = shift.Order(shift.Order.LIMIT_SELL, ticker,1, ask-eps)
            trader.submitOrder(limit_buy)
            trader.submitOrder(limit_sell)
            time.sleep(0.01)
            # cancel all pending orders
            while trader.getWaitingListSize() != 0:
                # print("Canceling Pending Orders!")
                for order in trader.getWaitingList():
                    if order.type == shift.Order.LIMIT_BUY:
                        order.type = shift.Order.CANCEL_BID
                    else:
                        order.type = shift.Order.CANCEL_ASK
                    trader.submitOrder(order)
                    time.sleep(0.1)
            print("Order Canceled!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    if i%(100)==0:
        while(True):
            # clear all the portfolio items with market sell
            for item in trader.getPortfolioItems().values():
                if item.getShares() > 0:
                    endSell = shift.Order(shift.Order.MARKET_SELL,
                                          item.getSymbol(),
                                          int(item.getShares() // 100))
                    trader.submitOrder(endSell)
            for item in trader.getPortfolioItems().values():
                if item.getShares() < 0:
                    endSell = shift.Order(shift.Order.MARKET_BUY,
                                          item.getSymbol(),
                                          int(-item.getShares() // 100))
                    trader.submitOrder(endSell)
            print(".\n")
            sum = 0.0
            for item in trader.getPortfolioItems().values():
                sum+=abs(item.getShares())
            if(sum==0):
                break
            else:
                time.sleep(0.1)
        print("portfolio clear!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")