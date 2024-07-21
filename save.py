# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 03:28:00 2024

@author: replica
"""

import FinanceDataReader as fdr
import pandas as pd

def code_to_symbol(df):
    df.rename(columns = {'Code' : 'Symbol'}, inplace = True)
    return df

def save_stock_list():
    fdr.StockListing('NASDAQ').to_csv('nasdaq.csv', index=False)
    fdr.StockListing('NYSE').to_csv('nyse.csv', index=False)
    fdr.StockListing('S&P500').to_csv('snp500.csv', index=False)
    code_to_symbol(fdr.StockListing('KOSPI')).to_csv('kospi.csv', index=False)
    code_to_symbol(fdr.StockListing('KOSDAQ')).to_csv('kosdaq.csv', index=False)
    fdr.StockListing('ETF/US').to_csv('etf_us.csv', index=False)
    fdr.StockListing('ETF/KR').to_csv('etf_kr.csv', index=False)
        
if __name__ == '__main__':
    save_stock_list()