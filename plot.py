# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 03:04:50 2024

@author: replica
"""
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import FinanceDataReader as fdr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_stocks_prices(stocks, start_date, end_date):
    t = datetime.strptime(end_date, '%Y-%m-%d')
    stocks_prices = {}
    for stock in stocks:
        try:
            stocks_prices[stock] = fdr.DataReader(stock, start_date, end_date)['Adj Close']
        except:
            stocks_prices[stock] = fdr.DataReader(stock, start_date, end_date)['Close']
    try:
        stocks_prices = pd.DataFrame(stocks_prices)
    except:
        t = t - timedelta(days = 1)
        end_date = t.strftime("%Y-%m-%d")
        stocks_prices = get_stocks_prices(stocks, start_date, end_date)
    return stocks_prices, t

def func(x, a, b):
    return a * np.exp(b * x)

def log_func(x, a, b):
    return np.log(func(x, a, b))

def binarize(x, std):
    if 1/(1+std*30) < x < (1+std*30):
        return 1
    else:
        return 0

def benchmark(cases, day, a, b, std):
    correct_cases = cases/func(day, a, b)
    correct_cases = correct_cases.apply(lambda x: binarize(x, std))
    return np.dot(correct_cases.T, day)

def draw_plot(stocks, start_date, end_date):
    stocks_prices, t = get_stocks_prices(stocks, start_date, end_date)
    n = int(len(stocks)**0.5) + 1
    stocks_prices_changes = stocks_prices.pct_change()
    fig, ax = plt.subplots(n, n, figsize=(15, 15), dpi=300)
    fig.suptitle('Stocks price ' + t.strftime("%Y-%m-%d"), fontsize=16)
    
    for i, stock in enumerate(stocks):
        cases = stocks_prices[stock].dropna()
        day = np.arange(0, len(cases))
        popt, pcov = curve_fit(func, day, cases, p0=(20, 0.0))
        a, b = popt
        log_popt, log_pcov = curve_fit(log_func, day, np.log(cases).replace([np.inf, -np.inf, np.nan], 0), p0=(20, 0.0))
        log_a, log_b = log_popt
        std = stocks_prices_changes[stock].std()
        if benchmark(cases, day, a, b, std) > benchmark(cases, day, log_a, log_b, std):
            ax[i//n, i%n].title.set_text("%s: %.1f, %.1f" % (stock, b*10000, std*1000))
            ax[i//n, i%n].plot(cases.index, func(day, a*(1+std*30), b), 'r-', alpha=0.5)
            ax[i//n, i%n].plot(cases.index, func(day, a*(1+std*15), b), 'r-', alpha=0.5)
            ax[i//n, i%n].plot(cases.index, func(day, a, b), 'r-', alpha=0.5)
            ax[i//n, i%n].plot(cases.index, func(day, a/(1+std*15), b), 'r-', alpha=0.5)
            ax[i//n, i%n].plot(cases.index, func(day, a/(1+std*30), b), 'r-', alpha=0.5)
        else:
            ax[i//n, i%n].title.set_text("%s: %.1f, %.1f" % (stock, log_b*10000, std*1000))
            ax[i//n, i%n].plot(cases.index, func(day, log_a*(1+std*30), log_b), 'g-', alpha=0.5)
            ax[i//n, i%n].plot(cases.index, func(day, log_a*(1+std*15), log_b), 'g-', alpha=0.5)
            ax[i//n, i%n].plot(cases.index, func(day, log_a, log_b), 'g-', alpha=0.5)
            ax[i//n, i%n].plot(cases.index, func(day, log_a/(1+std*15), log_b), 'g-', alpha=0.5)
            ax[i//n, i%n].plot(cases.index, func(day, log_a/(1+std*30), log_b), 'g-', alpha=0.5)
        ax[i//n, i%n].plot(cases.index, cases, 'b-', alpha=0.5)
        ax[i//n, i%n].tick_params(axis='x', labelrotation=90)
        ax[i//n, i%n].set_yscale('log')

    plt.subplots_adjust(left=0.125, bottom=-0.1, right=0.9, top=0.9, wspace=0.5, hspace=0.9)
    return fig