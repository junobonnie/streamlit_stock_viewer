# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 03:28:00 2024

@author: replica
"""

import FinanceDataReader as fdr
import pandas as pd

def save_stock_list():
    fdr.StockListing('NASDAQ').to_csv('nasdaq.csv', index=False)
    fdr.StockListing('NYSE').to_csv('nyse.csv', index=False)