import schedule
import time
import os
from save import save_stock_list
from multiprocessing import Process
def run_stock_viewer():
    os.system('streamlit run stock_viewer.py')
    
def run_save():
    os.system("pip install --upgrade pip")
    os.system("pip install -U yfinance")
    schedule.every().day.at("09:00").do(save_stock_list)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    process1 = Process(target=run_stock_viewer)
    process2 = Process(target=run_save)

    process1.start()
    process2.start()
