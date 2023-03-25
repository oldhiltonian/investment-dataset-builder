import pandas as pd
from .data_parser import DataParser
from .data_scraper import DataScraper
from typing import Dict, List, Tuple
import json
from pathlib import Path
import datetime as dt
import numpy as np
import requests
from IPython.display import clear_output
import time

key_path = Path().home() / "desktop" / "FinancialModellingPrep_API.txt"
with open(key_path) as file:
    api_key = file.read()

exchange_name_path = Path.cwd() / "investment_predictions" / "exchange_names.json"
with open(exchange_name_path, "r") as f:
    exchange_names_json = json.load(f)


class DatasetBuilder:
    """
    A class used to build a financial dataset from a given list of stock exchanges.

    Attributes:
        exchanges : List
            a list of stock exchanges
        possible_exchange_names : List
            a list of possible stock exchange names
        raw_data : List[Dict]
            a list of stock ticker data in dictionary format
        dataset : pd.DataFrame
            a pandas dataframe containing the built financial dataset
        _failed_tickers : List[str]
            a list of ticker symbols that could not be scraped
        _successful_tickers : List[str]
            a list of ticker symbols that were successfully scraped

    Methods:
        build()
            Fetches raw data from API and builds the financial dataset
        get_fmp_api_url() -> str
            Returns the API url for fetching stock ticker data
        make_stock_ticker_api_request(url: str) -> requests.Response
            Makes an API request for stock ticker data
        response_to_json(response_object) -> List[Dict]
            Converts API response object to a list of dictionaries
        fetch_raw_stock_ticker_data() -> List[Dict]
            Fetches raw stock ticker data from API
        set_exchanges(new_exchanges: List[str]='NASDAQ')
            Sets the exchanges attribute to a new list of stock exchanges
        check_valid_security(dct: Dict) -> bool
            Checks if the security is valid for the given exchanges
        build_dataset() -> pd.DataFrame
            Builds the financial dataset from the raw stock ticker data
        validate_data_is_float64(df) -> pd.DataFrame
            Validates that the data in the dataframe is of type float64

    """

    def __init__(self, exchanges: List=['New York Stock Exchange']):
        """
        Constructs all the necessary attributes for the DatasetBuilder object.

        Args:
            exchanges : List, optional
                a list of stock exchanges, by default None
        """
        self.exchanges = exchanges
        self.possible_exchange_names = exchange_names_json['exchange_names']
        self.copy=copy
        self.raw_data = None
        self.dataset = None
        
    def build(self):
        """
        Fetches raw data from API and builds the financial dataset.
        """
        self.raw_data = self.fetch_raw_stock_ticker_data()

        self.dataset = self.build_dataset()

    def get_fmp_api_url(self) -> str:
        """
        Returns the API url for fetching stock ticker data.

        Returns
            url: str
                the API url for fetching stock ticker data
        """
        url = f'https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}'
        return url
    
    @staticmethod
    def make_stock_ticker_api_request(url: str) -> requests.Response:
        """
        Makes an API request for stock ticker data.

        Parameters:
            url : str
                the API url for fetching stock ticker data

        Returns:
            requests.Response
                an API response object
        """
        response = requests.get(url)
        assert response.status_code == 200, f'API request failed: <{response.status_code}>'
        return response
    
    @staticmethod
    def response_to_json(response_object) -> List[Dict]:
        """
        Converts API response object to a list of dictionaries.

        Parameters:
            response_object : requests.Response
                an API response object

        Returns:
            List[Dict]
                a list of dictionaries containing the stock ticker data
        """
        return response_object.json()
    
    def fetch_raw_stock_ticker_data(self):
        """
        Fetches raw stock ticker data from API.

        Returns:
            List[Dict]
                a list of dictionaries containing the raw stock ticker data
        """
        url = self.get_fmp_api_url()
        response = self.make_stock_ticker_api_request(url)
        data = self.response_to_json(response)
        return data

    def set_exchanges(self, new_exchanges: List[str]='NASDAQ'):
        """
        Sets the exchanges attribute to a new list of stock exchanges.

        Parameters:
            new_exchanges : List[str], optional
                a list of new stock exchanges, by default 'NASDAQ'
        """
        for item in new_exchanges:
            assert str(item) in self.possible_exchange_names
        self.exchanges = new_exchanges

    def check_valid_security(self, dct: Dict):
        """
        Checks if the security is valid for the given exchanges.

        Parameters:
            dct : Dict
                a dictionary containing stock ticker data

        Returns:
            bool
                True if the security is valid for the given exchanges, False otherwise
        """
        if dct.get('type') == 'stock':
            if dct.get('exchange') in self.exchanges:
                return True
        return False

    def build_dataset(self) -> pd.DataFrame:
        """
        Builds the financial dataset from the raw stock ticker data.

        Returns:
            pd.DataFrame
                a pandas dataframe containing the built financial dataset
        """
        total_length = len(self.raw_data)
        self._failed_tickers = list()
        self._successful_tickers = list()
        total_df = None
        for idx, dct in enumerate(self.raw_data):
            # We only want to consider stocks
            is_valid = self.check_valid_security(dct)
            if not is_valid:
                continue
    
            ticker = dct['symbol']
            print(ticker)
            print(f'item: {idx}/{total_length}')
            
            try:
                scraper = DataScraper(ticker, api_key)
                parser = DataParser(scraper.data_dictionary)
            except AssertionError:
                self._failed_tickers.append(ticker)
                continue
            
            df = parser.final_data
            if total_df is None:
                    total_df = df
            else:
                total_df = pd.concat([total_df, df], axis=0)
            self._successful_tickers.append(ticker)
            clear_output()
        
        return total_df
                    
    def clean_up_dataframe(df):
        return df.drop(['start_date'], axis=1)

    # def validate_data_is_float64(self, df):
    #     ''' eed to redisgn this'''
    #     df = df.astype('float64')
    #     for col in df.columns:
    #         if df[col].dtype != 'float64':
    #             try:
    #                 df[col] = df[col].astype('float64')
    #             except:
    #                 continue
    #     return df

    

    

    

