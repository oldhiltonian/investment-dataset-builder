import yfinance as yf
from pandas_datareader import data as pdr
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Union
import requests
from requests import Response, Request
import json
from pathlib import Path
import datetime as dt

yf.pdr_override()


class CompanyDataScraper:
    """
    This class is used to scrape financial data from Financial Modeling Prep API and Yahoo Finance.

    Args:
        ticker (str): The ticker symbol for the stock to scrape data for.
        api_key (str, optional): The API key to access Financial Modeling Prep API. Defaults to "".
        period (str, optional): The period to retrieve data for. Can be 'annual' or 'quarter'. Defaults to 'quarter'.

    Attributes:
        ticker (str): The ticker symbol for the stock being scraped.
        period (str): The period to retrieve data for.
        api_key (str): The API key used to access Financial Modeling Prep API.
        fmp_api_requests (list): The list of available data types to retrieve from Financial Modeling Prep API.
        data_dictionary (dict): The dictionary of all data retrieved from Financial Modeling Prep API and Yahoo Finance.

    Raises:
        AssertionError: Raised if ticker, period, or api_key are not valid.

    """
    def __init__(self, ticker: str, api_key: str = "", period: str = "quarter"):
        self.ticker = ticker.upper()
        self.period = period.lower().strip()
        self.api_key = str(api_key)
        self.fmp_api_requests = ["info", "ratios", "metrics", "is"]
        self.assert_valid_user_inputs()
        self.data_dictionary = self.fetch_all_data()

    def assert_valid_user_inputs(self):
        """
        Asserts that the inputs for the DataScraper class are valid.

        Raises:
            AssertionError: Raised if ticker, period, or api_key are not valid.

        """
        assert self.ticker.isupper()
        assert self.period.islower()
        assert self.period in ["annual", "quarter"]
        assert self.api_key

    def get_fmp_api_url(self, data_type: str = "") -> str:
        """
        Returns the URL for a specific data type from Financial Modeling Prep API.

        Args:
            data_type (str, optional): The type of data to retrieve from Financial Modeling Prep API.

        Returns:
            str: The URL to retrieve the specified data type from Financial Modeling Prep API.

        Raises:
            AssertionError: Raised if the specified data_type is not valid.

        """
        assert data_type in self.fmp_api_requests, f"<{data_type}> invalid"
        if data_type == "ratios":
            template = (
                "https://financialmodelingprep.com/api/"
                "v3/ratios/{}?period={}&limit=400&apikey={}"
            )
            return template.format(self.ticker, self.period, self.api_key)
        if data_type == "metrics":
            template = (
                "https://financialmodelingprep.com/api/v3/"
                "key-metrics/{}?period={}&limit=400&apikey={}"
            )

            return template.format(self.ticker, self.period, self.api_key)
        if data_type == "info":
            template = (
                "https://financialmodelingprep.com/api/v3/" "profile/{}?apikey={}"
            )
            return template.format(self.ticker, self.api_key)
        if data_type == "is":
            template = (
                "https://financialmodelingprep.com/api/v3/"
                "income-statement/{}?period={}&limit=400&apikey={}"
            )
            return template.format(self.ticker, self.period, self.api_key)

    @staticmethod
    def make_fmp_api_requests(url: str) -> Response:
        """
        Makes an HTTP request to Financial Modeling Prep API and returns the response.

        Args:
            url (str): The URL to send the request to.

        Returns:
            Response: The response from the API request.

        Raises:
            AssertionError: Raised if the API request was unsuccessful.

        """
        fmp_response = requests.get(url)
        assert fmp_response.status_code == 200, "Request unsuccessful"
        return fmp_response

    @staticmethod
    def convert_raw_data_to_json(response: Response) -> Dict:
        """
        Converts the response from an API request to a JSON object.

        Args:
            response (Response): The response object from the API request.

        Returns:
            dict: A dictionary representing the JSON object returned by the API request.

        Raises:
            AssertionError: Raised if the API request was successful but the response was empty.

        """
        json_data = response.json()
        assert len(json_data) > 0, "API request successful but empty"
        return json_data

    def fetch_stock_price_data(self) -> pd.DataFrame:
        """
        Fetches stock price data from Yahoo Finance.

        Returns:
            pandas.DataFrame: A DataFrame containing the stock price data.

        Raises:
            AssertionError: Raised if there is insufficient stock price data.

        """
        start = dt.date(1970, 1, 1)
        stock_data = pdr.get_data_yahoo(self.ticker, start=start, interval="1d")
        assert len(stock_data) > 85, "Insufficient stock price data"
        return stock_data

    def fetch_all_data(self) -> Dict[str, Dict]:
        """
        Fetches all financial data from Financial Modeling Prep API and Yahoo Finance.

        Returns:
            dict: A dictionary containing all the financial data retrieved.

        Raises:
            AssertionError: Raised if there is insufficient stock price data or if the API request is unsuccessful.

        """
        data_dictionary = {}
        for string in self.fmp_api_requests:
            url = self.get_fmp_api_url(string)
            response = self.make_fmp_api_requests(url)
            data = self.convert_raw_data_to_json(response)
            data_dictionary[string] = data
        stock_price_data = self.fetch_stock_price_data()
        data_dictionary["price"] = [stock_price_data]
        return data_dictionary


class EconomicDataScraper:

    '''Change to inherit from CompanyDataScraper and just redefine the
    appropriate methods?'''

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def get_fmp_api_url(self, data_type: str) -> str:
        end = str(dt.date.today())
        if data_type == 'TYield':
            template = "https://financialmodelingprep.com/api/v4/"\
                          "treasury?from=1970-06-30&to={}&apikey={}"
            return template.format(end, self.api_key)
        if data_type in ['CPI', 'realGDP', 'consumerSentiment']:
            template = "https://financialmodelingprep.com/api/v4/"\
                         "economic?name={}&from=1970-06-30&to={}&apikey={}"
            return template.format(data_type, end, self.api_key)
        
    def fetch_snp500_historical_prices(self) -> pd.DataFrame:
        start = dt.date(1970, 1, 1)
        df = pdr.get_data_yahoo('^GSPC', start=start, interval='1d')
        assert len(df) > 85, "Insufficient stock price data"
        return df
