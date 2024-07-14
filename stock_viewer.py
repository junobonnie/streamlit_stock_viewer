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
    st.session_state.candidates = process.extract(stock_, pd.concat([total_market['Symbol'], total_market['Name']], axis = 0), limit=10)
    st.session_state.stock_ = ""
    
def add_stock_(stock_, stock_name_):
    if not stock_ in st.session_state.stocks:
        st.session_state.stocks.append([stock_, stock_name_])
    st.session_state.candidates = []
    st.experimental_rerun()

def delete_all():
    st.session_state.stocks = []
    st.experimental_rerun()

schedule.every().day.at("09:00").do(save_stock_list)

end_date = datetime.now().strftime("%Y-%m-%d")

if 'stocks' not in st.session_state:
    st.session_state.stocks = []

if 'nasdaq' not in st.session_state:
    try:
        st.session_state.nasdaq = pd.read_csv('nasdaq.csv')
        st.session_state.nyse = pd.read_csv('nyse.csv')
        st.session_state.kospi = pd.read_csv('kospi.csv')
        st.session_state.kosdaq = pd.read_csv('kosdaq.csv')
        st.session_state.etf_us = pd.read_csv('etf_us.csv')
        st.session_state.etf_kr = pd.read_csv('etf_kr.csv')
    except:
        save_stock_list()
        st.session_state.nasdaq = pd.read_csv('nasdaq.csv')
        st.session_state.nyse = pd.read_csv('nyse.csv')
        st.session_state.kospi = pd.read_csv('kospi.csv')
        st.session_state.kosdaq = pd.read_csv('kosdaq.csv')
        st.session_state.etf_us = pd.read_csv('etf_us.csv')
        st.session_state.etf_kr = pd.read_csv('etf_kr.csv')
        
total_market = pd.concat([st.session_state.nasdaq, 
                          st.session_state.nyse, 
                          st.session_state.kospi, 
                          st.session_state.kosdaq,
                          st.session_state.etf_us,
                          st.session_state.etf_kr], ignore_index=True)

us_index = [['IXIC','나스닥'], ['DJI','다우존스'], ['S&P500','S&P500'],
              ['RUT', '러셀2000'], ['VIX', 'VIX']]

kr_index = [['KS11','코스피'], ['KQ11','코스닥'], ['KS200','코스피200']]

fred = [['FRED:NASDAQCOM','나스닥종합지수'], ['FRED:ICSA','주간 실업수당 청구 건수'], 
        ['FRED:UMCSENT','소비자심리지수'], ['FRED:HSN1F','주택 판매 지수'], 
        ['FRED:UNRATE','실업률'], ['FRED:M2SL','M2 통화량'], 
        ['FRED:BAMLH0A0HYM2','하이일드 채권 스프레드'], ['FRED:CPIAUCSL','소비자 물가 지수'], 
        ['FRED:PCE','개인소비지출'], ['FRED:FEDFUNDS','미국기준금리']]

st.title('Stock log graph')

ep = st.expander('USA')
cols = ep.columns(2)
cols[0].subheader('Nasdaq')
cols[0].dataframe(st.session_state.nasdaq)
cols[1].subheader('Nyse')
cols[1].dataframe(st.session_state.nyse)

ep = st.expander('KOREA')
cols = ep.columns(2)
cols[0].subheader('Kospi')
cols[0].dataframe(st.session_state.kospi)
cols[1].subheader('Kosdaq')
cols[1].dataframe(st.session_state.kosdaq)

ep = st.expander('ETF(US & KR)')
cols = ep.columns(2)
cols[0].subheader('USA')
cols[0].dataframe(st.session_state.etf_us)
cols[1].subheader('KOREA')
cols[1].dataframe(st.session_state.etf_kr)

ep = st.expander('INDEX(US & KR)')
cols = ep.columns(2)
ct = cols[0].container()
ct.subheader('USA')
for i, us_index_ in enumerate(us_index):
    if ct.button('%s(%s)'%(us_index_[0], us_index_[1]), key='a%d'%i):
        add_stock_(us_index_[0], us_index_[1])
ct = cols[1].container()
ct.subheader('KOREA')
for i, kr_index_ in enumerate(kr_index):
    if ct.button('%s(%s)'%(kr_index_[0], kr_index_[1]), key='b%d'%i):
        add_stock_(kr_index_[0], kr_index_[1])
        
ep = st.expander('FRED')
for i, fred_ in enumerate(fred):
    if ep.button('%s(%s)'%(fred_[0].replace('FRED:',''), fred_[1]), key='c%d'%i):
        add_stock_(fred_[0], fred_[1])
        
st.subheader('Set the config')
cols = st.columns(2)
cols[0].text_input('Search a stock ticker', key='stock_', on_change=guess_stock_)
start_date = datetime.strptime('2008-01-01', '%Y-%m-%d')
st.session_state.start_date = cols[1].date_input('Start Date input', start_date)

if 'candidates' in st.session_state:
    cols = st.columns(1)
    for i, cadidate in enumerate(st.session_state.candidates):
        index = cadidate[2]
        if cols[0].button('%s(%s)'%(total_market['Symbol'][index],total_market['Name'][index]), key='d%d'%i):
            add_stock_(total_market['Symbol'][index], total_market['Name'][index])

st.subheader('Delete ticker')
num_stocks = len(st.session_state.stocks)
num_cols = 6
for i in range(0, num_stocks, num_cols):
    cols = st.columns(num_cols)
    for j in range(num_cols):
        if i + j < num_stocks:
            stock = st.session_state.stocks[i+j]
            print('%s(%s)'%(stock[0], stock[1]))
            if cols[j].button('%s(%s)'%(stock[0], stock[1]), key=i+j):
                del st.session_state.stocks[i+j]
                st.experimental_rerun()
                
st.subheader('Delete all')
if st.button('Delete all'):
    delete_all()

st.subheader('Draw a plot')

if st.button('Draw a plot'):
    for stock in st.session_state.stocks:
        st.pyplot(draw_plot(stock[0], stock[1], st.session_state.start_date, end_date))