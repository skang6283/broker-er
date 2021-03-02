import os
import time
from datetime import date
import argparse
from tqdm import tqdm

import numpy as np
import pandas as pd

import yfinance as yf
from get_all_tickers import get_tickers
import requests


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = 'data'
NUM_COMPANY = 500
STOCK_DATA_LENGTH = '2y'

class YFinanceDownLoader:
    def __init__(self, num_company, stock_data_length):
        self.num_company = num_company
        self.stock_data_length = stock_data_length
        self.build_top_n_tickers()

    def build_top_n_tickers(self):
        # Get a list of top N US stock tickers
        print(f"Start fetching top {self.num_company} stock tickers")
        self.list_top_n_tickers = get_tickers.get_biggest_n_tickers(self.num_company)
        print(f"Finished")

    def get_daily_stock_data(self):
        # Get stock history data
        print(f"Start downloading top {self.num_company} stock data with length {self.stock_data_length}")
        data = pd.DataFrame()
        pbar = tqdm(range(len(self.list_top_n_tickers)))
        for tick in self.list_top_n_tickers:

            # Get individual stock data from yahoo finance API
            stock_data = yf.Ticker(tick)
            df = stock_data.history(period=self.stock_data_length)

            # Add stock symbol (ticker) 
            df.insert(0, 'Ticker', tick)

            # Concat data
            data = pd.concat([df, data]) 
            
            pbar.update(1)
            time.sleep(1) # Avoid getting banned from yahoo finance

        pbar.close()

        # Save data in to .csv
        data = data.reset_index()
        file_name = f'top{self.num_company}_{self.stock_data_length}_{date.today().strftime("%b-%d-%Y")}_stock_data.csv'
        save_path = os.path.join(ROOT_DIR, DATA_DIR, file_name)
        data.to_csv(save_path, index=False, header=True)
        print(f"Data file located at {save_path}")

    def get_stock_info(self):
        print(f"Start downloading top {self.num_company} stock data with length {self.stock_data_length}")
        data = pd.DataFrame()
        pbar = tqdm(range(len(self.list_top_n_tickers)))
        for tick in self.list_top_n_tickers:

            # Get individual stock data from yahoo finance API
            stock_data = yf.Ticker(tick)
            try:
                info = stock_data.info

                # TODO: solve issues with both array and scalar in dictionary values
                del info['companyOfficers']
                df = pd.DataFrame(stock_data.info, index=[0])

                # Add stock symbol (ticker) 
                df.insert(0, 'Ticker', tick)

                # Concat data
                data = pd.concat([df, data]) 
            except:
                print(f"Failed to get stock info {tick}")
                
            pbar.update(1)
            time.sleep(1) # Avoid getting banned from yahoo finance

        pbar.close()
        # Save data in to .csv
        data = data.reset_index()
        file_name = f'top{self.num_company}_stock_info.csv'
        save_path = os.path.join(ROOT_DIR, DATA_DIR, file_name)
        data.to_csv(save_path, index=False, header=True)
        print(f"Data file located at {save_path}")


if __name__ == "__main__":
    downloader = YFinanceDownLoader(NUM_COMPANY, STOCK_DATA_LENGTH)
    

    # Download daily stock data
    # downloader.get_daily_stock_data()

    # Download stock basic info
    downloader.get_stock_info()
    








