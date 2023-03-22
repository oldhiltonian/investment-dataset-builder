import pandas as pd
from .data_parser import DataParser
from .data_scraper import DataScraper
from typing import Dict, List, Tuple
import json
from pathlib import Path
import datetime as dt
import numpy as np
import requests

key_path = Path().home() / "desktop" / "FinancialModellingPrep_API.txt"
with open(key_path) as file:
    api_key = file.read()

exchange_name_path = Path.cwd() / "investment_predictions" / "exchange_names.json"
with open(exchange_name_path, "r") as f:
    exchange_names = json.load(f)


class DatasetBuilder:
    def __init__(self, exchanges: List=None):
        self.exchanges = exchanges
        self.possible_exchange_names = exchange_names['exchange_names']
        self.raw_data = self.fetch_raw_stock_ticker_data()

    def build(self):
        self.dataset = self.build_dataset()

    def get_fmp_api_url(self) -> str:
        url = f'https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}'
        return url
    
    @staticmethod
    def make_stock_ticker_api_request(url: str) -> requests.Response:
        response = requests.get(url)
        assert response.status_code == 200, f'API request failed: <{response.status_code}>'
        return response
    
    @staticmethod
    def response_to_json(response_object) -> List[Dict]:
        return response_object.json()
    
    def fetch_raw_stock_ticker_data(self):
        url = self.get_fmp_api_url()
        response = self.make_stock_ticker_api_request(url)
        data = self.response_to_json(response)
        return data

    def set_exchanges(self, new_exchanges: List[str]='NASDAQ'):
        for item in new_exchanges:
            assert str(item) in self.possible_exchange_names
        self.exchanges = new_exchanges

    def build_dataset(self) -> pd.DataFrame:
        self._failed_tickers = list()
        trigger = None
        for dct in self.raw_data:
            # We only want to consider stocks
            if dct['type'] != 'stock':
                continue
            
            ticker = dct['symbol']
            
            if dct['exchange'] in self.exchanges:
                if not trigger:
                    try:
                        initial = DataParser(DataScraper(ticker, api_key).data_dictionary)
                        total_df = initial.final_data
                        trigger = True
                    except AssertionError:
                        self._failed_tickers.append(ticker)
                        continue
                else:
                    try:
                        new_parser = DataParser(DataScraper(ticker, api_key).data_dictionary)
                        new_df = new_parser.final_data
                        total_df = pd.concat([total_df, new_df], axis=0)
                    except:
                        self._failed_tickers.append(ticker)
                        continue
        return total_df
                    
    def data_validation(self):
        # Drop all instances where the priceRatioToSNP is nan
        # Drop date, period, start date
        # zero all values that are nan
        # ensure all cells are float
        pass

    

    

    

