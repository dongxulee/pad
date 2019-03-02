import sys
import numpy as np
import pandas as pd
import shift
import time
import math as ma
import matplotlib.pyplot as plt
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt import discrete_allocation
sys.path.insert(0, 'include')


def efficient_frontier(trader, portfolio, assigned_value, target_risk):
    # Get data set from universe
    hist_price = pd.DataFrame()
    stock_list = trader.getStockList()
    for ticker in stock_list:
        hist_price = pd.concat([hist_price, portfolio[ticker]['Last']], axis=1).rename(columns={'Last': ticker})

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(hist_price)
    S = risk_models.sample_cov(hist_price)

    # Optimise for target risk
    ef = EfficientFrontier(mu, S, weight_bounds=(-1, 1))
    raw_weights = ef.efficient_risk(target_risk=target_risk, market_neutral=False)
    cleaned_weights = ef.clean_weights()

    # Calculate the actual allocation
    sum = 0
    switched_weights = {}
    for ticker in stock_list:
        sum = sum + abs(cleaned_weights[ticker])
    for ticker in stock_list:
        switched_weights[ticker] = cleaned_weights[ticker] * 1 / sum

    latest_prices = discrete_allocation.get_latest_prices(hist_price)
    allocation = {}
    leftover = assigned_value
    for ticker in stock_list:
        allocation[ticker] = np.sign(switched_weights[ticker]) * \
                             ma.floor(assigned_value *
                                      abs(switched_weights[ticker]) / (100 * latest_prices[ticker]))
        leftover = leftover - abs(allocation[ticker]) * latest_prices[ticker] * 100

    # Operation
    portfolio_items = {}
    adjustment = {}
    for ticker in stock_list:
        portfolio_items[ticker] = 0
    for item in trader.getPortfolioItems().values():
        portfolio_items[item.getSymbol()] = item.getShares()
    for ticker in stock_list:
        adjustment[ticker] = allocation[ticker] - portfolio_items[ticker]

    for ticker in stock_list:
        if adjustment[ticker] > 0:
            marketBuy = shift.Order(shift.Order.MARKET_BUY, ticker, adjustment[ticker])
            trader.submitOrder(marketBuy)
        if adjustment[ticker] < 0:
            marketSell = shift.Order(shift.Order.MARKET_SELL, ticker, abs(adjustment[ticker]))
            trader.submitOrder(marketSell)

    # Monitor
    print(cleaned_weights)
    ef.portfolio_performance(verbose=True)
    print(allocation)
    print("Funds remaining: ${:.2f}".format(leftover))
