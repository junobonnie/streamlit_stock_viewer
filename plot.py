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
import plotly.express as px
import yfinance as yf

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False

def get_stock_prices(stock, start_date, end_date):
    if 'FRED:' in stock:
        stock_prices = fdr.DataReader(stock, start_date, end_date)[stock.replace('FRED:', '')]
    else:
        try:
            stock_prices = fdr.DataReader(stock, start_date, end_date)['Adj Close']
        except:
            stock_prices = fdr.DataReader(stock, start_date, end_date)['Close']
    return stock_prices

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

def draw_plot(stock, stock_name, start_date, end_date, is_log=True):
    stock_prices = get_stock_prices(stock, start_date, end_date)
    stock_prices_changes = stock_prices.pct_change()
    fig = plt.figure(figsize=(9, 3), dpi=100)
    ax = fig.add_subplot(1,1,1)
    ax.set_title('Stock price ' + end_date, fontsize=16)
    
    cases = stock_prices.dropna()
    day = np.arange(0, len(cases))
    popt, pcov = curve_fit(func, day, cases, p0=(20, 0.0))
    a, b = popt
    log_popt, log_pcov = curve_fit(log_func, day, np.log(cases).replace([np.inf, -np.inf, np.nan], 0), p0=(20, 0.0))
    log_a, log_b = log_popt
    std = stock_prices_changes.std()
    if benchmark(cases, day, a, b, std) > benchmark(cases, day, log_a, log_b, std):
        ax.title.set_text("%s   %s: %.1f, %.1f" % (end_date, stock_name, b*10000, std*1000))
        ax.plot(cases.index, func(day, a*(1+std*30), b), 'r-', alpha=0.5)
        ax.plot(cases.index, func(day, a*(1+std*15), b), 'r-', alpha=0.5)
        ax.plot(cases.index, func(day, a, b), 'r-', alpha=0.5)
        ax.plot(cases.index, func(day, a/(1+std*15), b), 'r-', alpha=0.5)
        ax.plot(cases.index, func(day, a/(1+std*30), b), 'r-', alpha=0.5)
    else:
        ax.title.set_text("%s   %s: %.1f, %.1f" % (end_date, stock_name, log_b*10000, std*1000))
        ax.plot(cases.index, func(day, log_a*(1+std*30), log_b), 'g-', alpha=0.5)
        ax.plot(cases.index, func(day, log_a*(1+std*15), log_b), 'g-', alpha=0.5)
        ax.plot(cases.index, func(day, log_a, log_b), 'g-', alpha=0.5)
        ax.plot(cases.index, func(day, log_a/(1+std*15), log_b), 'g-', alpha=0.5)
        ax.plot(cases.index, func(day, log_a/(1+std*30), log_b), 'g-', alpha=0.5)
    ax.plot(cases.index, cases, 'b-', alpha=0.5)
    ax.tick_params(axis='x', labelrotation=90)
    if is_log:
        ax.set_yscale('log')
    ax.grid(visible=True)
    plt.subplots_adjust(left=0.125, bottom=-0.1, right=0.9, top=0.9, wspace=0.5, hspace=0.9)
    return fig

def get_stock_change(stock, deltatime):
    history = yf.Ticker(stock).history(interval='1d', period=deltatime)
    if history.empty:
        history = yf.Ticker(stock).history(interval='1d', period='max')
    return history['Close'][-1], (history['Close'][-1] - history['Open'][0])/history['Open'][0] 

def new_colorbar(deltatime):
    if deltatime == '1d':
        value = 0.03
    elif deltatime == '5d':
        value = 0.06
    elif deltatime == '1mo':
        value = 0.1
    elif deltatime == '3mo':
        value = 0.2
    elif deltatime == '6mo':
        value = 0.25
    elif deltatime == '1y':
        value = 0.3
    elif deltatime == '5y':
        value = 3.0
    range_color = (-value, value)
    tickvals = [-value, 0, value]
    string = str(int(value*100))
    ticktext = ['-%s%%'%string, '0%', '%s%%'%string]
    return range_color, tickvals, ticktext

def draw_stock_map(market, deltatime):
    stocks = pd.read_csv('snp500.csv')
    stock_map = {}
    stock_map["Sector"] = []
    stock_map["Industry"] = []
    stock_map["Symbol"] = []
    stock_map["Name"] = []
    stock_map["Price"] = []
    stock_map["Change"] = []
    stock_map['marketCap'] = []
    for stock in stocks['Symbol']:
        ticker = yf.Ticker(stock).info
        if not 'sector' in ticker:
            stock = stock[:-1] + '-' + stock[-1]
            ticker = yf.Ticker(stock).info
        stock_map['Sector'].append(ticker['sector'])
        stock_map['Industry'].append(ticker['industry'])
        stock_map["Symbol"].append(stock)
        stock_map["Name"].append(ticker['longName'])
        price, change = get_stock_change(stock, deltatime)
        stock_map["Price"].append(price)
        stock_map["Change"].append(change)
        stock_map['marketCap'].append(ticker['marketCap'])
    stock_map = pd.DataFrame(stock_map)
    range_color, tickvals, ticktext = new_colorbar(deltatime)
    fig = px.treemap(stock_map, path=[px.Constant("S&P500"), 'Sector', 'Industry','Symbol'], values='marketCap',
                  color='Change', hover_data=['Change','Symbol'], 
                  range_color=range_color, color_continuous_scale=[[0, 'rgb(246, 53, 56)'], [0.5, 'rgb(65, 69, 84)'], [1, 'rgb(48, 204, 90)']])
    stock_map.sort_values(by=['Symbol', 'Industry', 'Sector'], inplace=True)

    text = ['<b style="font-size:25px">%s<br><br>%.2f%%</b>'%(i, 100*stock_map[stock_map['Symbol']==i]['Change']) for i in stock_map['Symbol']]
    hovertext = ['Name: %s <br> Price: $%.2f'%(stock_map[stock_map['Symbol']==i]['Name'].values[0], stock_map[stock_map['Symbol']==i]['Price']) for i in stock_map['Symbol']]
    
    fig.update_traces(textposition='middle center', text = text, textinfo = 'text')
    fig.update_traces(textfont_color='white',textfont_size=15, hovertemplate='<b>%{label}</b> <br>%{hovertext} <br>Change: %{value}', hovertext=hovertext)
    fig.update_layout(margin = dict(t=30, l=5, r=5, b=5), height=600)
    fig.update_coloraxes(colorbar={'tickvals': tickvals, 'ticktext': ticktext, 'orientation':'h', 'thickness':20, 'y': -0.12})
    return fig#write_html("file.html")#write_image('./test.png')

if __name__ == "__main__":
    stock = 'MSFT'
    name = "Microsoft"
    start_date = '2024-07-01'
    end_date = '2024-07-20'
    # draw_plot(stock, name, start_date, end_date)
    
    
    
    
    