# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 19:24:19 2024

@author: replica
"""

import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime
import streamlit as st
from thefuzz import process
from plot import draw_plot
from save import save_stock_list
import schedule

def guess_stock_():
    stock_ = st.session_state.stock_#.upper()
    total_market = pd.concat([st.session_state.nasdaq, st.session_state.nyse], ignore_index=True)
    st.session_state.candidates = process.extract(stock_, pd.concat([total_market['Symbol'], total_market['Name']], axis = 0), limit=10)
    st.session_state.stock_ = ""
    
def add_stock_(stock_):
    if not stock_ in st.session_state.stocks:
        st.session_state.stocks.append(stock_)
    st.session_state.candidates = []
    st.experimental_rerun()

def delete_all():
    st.session_state.stocks = []
    st.experimental_rerun()

schedule.every().day.at("09:00").do(save_stock_list)

end_date = datetime.now().strftime("%Y-%m-%d")

if 'stocks' not in st.session_state:
    st.session_state.stocks = ['IXIC', 'DJI', 'TQQQ', 'QQQ', 'DDM', 'SPY']

if 'nasdaq' not in st.session_state:
    st.session_state.nasdaq = pd.read_csv('nasdaq.csv')
    st.session_state.nyse = pd.read_csv('nyse.csv')
    
st.title('Stock log graph')

cols = st.columns(2)

cols[0].subheader('Nasdaq')
cols[0].dataframe(st.session_state.nasdaq)
cols[1].subheader('Nyse')
cols[1].dataframe(st.session_state.nyse)

st.subheader('Set the config')
cols = st.columns(2)
cols[0].text_input('Search a stock ticker', key='stock_', on_change=guess_stock_)
start_date = datetime.strptime('2008-01-01', '%Y-%m-%d')
st.session_state.start_date = cols[1].date_input('Start Date input', start_date)

if 'candidates' in st.session_state:
    cols = st.columns(1)
    for i, cadidate in enumerate(st.session_state.candidates):
        index = cadidate[2]
        total_market = pd.concat([st.session_state.nasdaq, st.session_state.nyse], ignore_index=True)
        if cols[0].button('%s(%s)'%(total_market['Symbol'][index],total_market['Name'][index]), key='a%d'%i):
            add_stock_(total_market['Symbol'][index])

st.subheader('Delete ticker')
num_stocks = len(st.session_state.stocks)
num_cols = 6
for i in range(0, num_stocks, num_cols):
    cols = st.columns(num_cols)
    for j in range(num_cols):
        if i + j < num_stocks:
            if cols[j].button(st.session_state.stocks[i+j], key=i+j):
                del st.session_state.stocks[i+j]
                st.experimental_rerun()
                
st.subheader('Delete all')
if st.button('Delete all'):
    delete_all()

st.subheader('Draw a plot')

if st.button('Draw a plot'):
    st.pyplot(draw_plot(st.session_state.stocks, st.session_state.start_date, end_date))