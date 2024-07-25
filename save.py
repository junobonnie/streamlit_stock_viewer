# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 03:28:00 2024

@author: replica
"""

import FinanceDataReader as fdr
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from math import isnan

def get_stock_history(ticker):
    history = ticker.history(interval='1d', period='5y')
    if history.empty:
        history = ticker.history(interval='1d', period='max')
    return history

def get_stock_change(history, deltatime):
    if deltatime == '1d':
        if len(history) > 1:
            return (history['Close'][-1] - history['Close'][-2])/history['Close'][-2]
        else:
            return (history['Close'][-1] - history['Close'][0])/history['Close'][0]
    elif deltatime == '5d':
        if len(history) > 5:
            return (history['Close'][-1] - history['Close'][-6])/history['Close'][-6]
        else:
            return (history['Close'][-1] - history['Close'][0])/history['Close'][0]
    elif deltatime == '1mo':
        history = history[(datetime.now()-timedelta(days=30)).strftime("%Y-%m-%d"):]
        return  (history['Close'][-1] - history['Close'][0])/history['Close'][0]
    elif deltatime == '3mo':
        history = history[(datetime.now()-timedelta(days=91)).strftime("%Y-%m-%d"):]
        return  (history['Close'][-1] - history['Close'][0])/history['Close'][0]
    elif deltatime == '6mo':
        history = history[(datetime.now()-timedelta(days=182)).strftime("%Y-%m-%d"):]
        return  (history['Close'][-1] - history['Close'][0])/history['Close'][0]
    elif deltatime == '1y':
        history = history[(datetime.now()-timedelta(days=365)).strftime("%Y-%m-%d"):]
        return  (history['Close'][-1] - history['Close'][0])/history['Close'][0]
    elif deltatime == '5y':
        if isnan(history['Close'][0]):
            return (history['Close'][-1] - history['Close'][1])/history['Close'][1]
        return  (history['Close'][-1] - history['Close'][0])/history['Close'][0]
    
def save_stock_map():
    stocks = pd.read_csv('snp500.csv')
    stock_map = {}
    stock_map["Symbol"] = []
    stock_map["Name"] = []
    stock_map["Industry"] = []
    stock_map["Sector"] = []
    stock_map['marketCap'] = []
    stock_map["Price"] = []
    deltatimes = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '5y']
    for deltatime in deltatimes:
        stock_map[deltatime+"_Change"] = []

    for stock in stocks['Symbol']:
        ticker = yf.Ticker(stock)
        info = ticker.info
        if not 'sector' in ticker.info:
            stock = stock[:-1] + '-' + stock[-1]
            ticker = yf.Ticker(stock)
            info = ticker.info
        stock_map["Symbol"].append(stock)
        stock_map["Name"].append(info['longName'])
        stock_map['Industry'].append(info['industry'])
        stock_map['Sector'].append(info['sector'])
        stock_map['marketCap'].append(info['marketCap'])
        history = get_stock_history(ticker)
        price = history['Close'][-1]
        stock_map["Price"].append(price)
        for deltatime in deltatimes:
            change = get_stock_change(history, deltatime)
            stock_map[deltatime+"_Change"].append(change)
           
    stock_map = pd.DataFrame(stock_map)
    stock_map.to_csv('snp500_map.csv', index=False)

def code_to_symbol(df):
    df.rename(columns = {'Code' : 'Symbol'}, inplace = True)
    return df

def save_stock_list():
    fdr.StockListing('NASDAQ').to_csv('nasdaq.csv', index=False)
    fdr.StockListing('NYSE').to_csv('nyse.csv', index=False)
    fdr.StockListing('S&P500').to_csv('snp500.csv', index=False)
    code_to_symbol(fdr.StockListing('KOSPI')).to_csv('kospi.csv', index=False)
    code_to_symbol(fdr.StockListing('KOSDAQ')).to_csv('kosdaq.csv', index=False)
    try:
        fdr.StockListing('ETF/US').to_csv('etf_us.csv', index=False)
    except:
        print("Unexpected Error!")
        pass
    try:
        fdr.StockListing('ETF/KR').to_csv('etf_kr.csv', index=False)
    except:
        print("Unexpected Error!")
        pass
    save_stock_map()
    print('Log: Stock list saved')
        
if __name__ == '__main__':
    save_stock_list()