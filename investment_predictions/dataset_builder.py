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
        self.raw_data = None
        self.dataset = None
        
    def build(self):
        self.raw_data = self.fetch_raw_stock_ticker_data()
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

    def check_valid_security(self, dct: Dict):
        if dct.get('type') == 'stock':
            if dct.get('exchange') in self.exchanges:
                return True
        return False

    def build_dataset(self) -> pd.DataFrame:
        self._failed_tickers = list()
        self._successful_tickers = list()
        total_df = None
        for dct in self.raw_data:
            # We only want to consider stocks
            is_valid = self.check_valid_security(dct)
            if not is_valid:
                continue
    
            ticker = dct['symbol']
            
            try:
                scraper = DataScraper(ticker, api_key)
                parser = DataParser(scraper.data_dictionary)
            except AssertionError:
                self._failed_tickers.append(ticker)
            
            df = parser.final_data
            if total_df is None:
                    total_df = df
            else:
                total_df = pd.concat([total_df, df], axis=0)
            self._successful_tickers.append(ticker)
        
        return total_df
                    
    def data_validation(self):
        # Drop all instances where the priceRatioToSNP is nan
        # Drop date, period, start date
        # zero all values that are nan
        # ensure all cells are float
        pass

    

    

    

