import sys
import numpy as np
import pandas as pd
import shift
import math as ma
from include.pypfopt.efficient_frontier import EfficientFrontier
from include.pypfopt import risk_models
from include.pypfopt import expected_returns
from include.pypfopt import discrete_allocation
sys.path.insert(0, 'include')


def efficient_frontier(tickers, trader, stockList, assigned_value=1000000 / 3, target_risk=0.2):
    # Get data set from universe
    hist_price = pd.DataFrame()
    for ticker in tickers:
        hist_price = pd.concat([hist_price, stockList[ticker].historicalData(100)['lastPrice']], axis=1).rename(columns={'lastPrice': ticker})
    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(hist_price)
    S = risk_models.sample_cov(hist_price)

    # Optimise for target risk
    ef = EfficientFrontier(mu, S, weight_bounds=(-0.1, 0.1))
    raw_weights = ef.efficient_risk(target_risk=target_risk, market_neutral=False)
    cleaned_weights = ef.clean_weights()
    # Calculate the actual allocation
    sum = 0
    switched_weights = {}
    for ticker in tickers:
        sum = sum + abs(cleaned_weights[ticker])
    for ticker in tickers:
        switched_weights[ticker] = cleaned_weights[ticker] * 1 / sum

    latest_prices = discrete_allocation.get_latest_prices(hist_price)
    allocation = {}
    leftover = assigned_value
    for ticker in tickers:
        allocation[ticker] = np.sign(switched_weights[ticker]) * \
                             ma.floor(assigned_value *
                                      abs(switched_weights[ticker]) / (100 * latest_prices[ticker]))
        leftover = leftover - abs(allocation[ticker]) * latest_prices[ticker] * 100

    # Operation
    portfolio_items = {}
    adjustment = {}
    for ticker in tickers:
        portfolio_items[ticker] = 0
    for ticker in tickers:
        item = trader.getPortfolioItem(ticker)
        portfolio_items[ticker] = int(item.getShares()//100)
    for ticker in tickers:
        adjustment[ticker] = allocation[ticker] - portfolio_items[ticker]

    for ticker in tickers:
        if adjustment[ticker] > 0:
            marketBuy = shift.Order(shift.Order.MARKET_BUY, ticker, int(adjustment[ticker]))
            trader.submitOrder(marketBuy)
        if adjustment[ticker] < 0:
            marketSell = shift.Order(shift.Order.MARKET_SELL, ticker, int(abs(adjustment[ticker])))
            trader.submitOrder(marketSell)

    # Monitor
    print(cleaned_weights)
    ef.portfolio_performance(verbose=True)
    print(allocation)
    print("Funds remaining: ${:.2f}".format(leftover))
