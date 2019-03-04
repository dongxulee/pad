from marketMaker import marketMaker

def dongxuStrategy(tickers, trader, stockList):
    # 90% informed trader in the market.
    alpha = 0.9
    # set noise to be 0.01
    noise = 0.01
    # dictionary contain all market makers.
    marketMakers = dict()
    for ticker in tickers:
        marketMakers[ticker] = marketMaker(ticker, alpha, noise)