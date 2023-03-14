import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Union
import requests
from requests import Response, Request
import json
from pathlib import Path


key_path = Path().home() / "desktop" / "FinancialModellingPrep_API.txt"
with open(key_path) as file:
    api_key = file.read()

class DataScraper:
    def __init__(self, ticker: str, period: str='quarter'):
        self.ticker = ticker.upper()
        self.period = period.lower().strip()
        self.fmp_api_requests = ['ratios', 'metrics', 'info', 'is']
        # TODO: assert period is in [annual, quarter]

    @staticmethod
    def multi_line_string_stripper(string: str) -> str:
        # TODO: strip and replace all whitespace and newlines with ''
        string_ = string.replace(' ', '').replace('\t', '')
        string_ = string_.replace('\n', '').replace
        pass

    def get_fmp_api_url(self, data_type: str='') -> str:
        assert data_type in self.fmp_api_requests, f"<{data_type}> invalid"
        if data_type == 'ratios':
            template = "https://financialmodelingprep.com/api/"\
                        "v3/ratios/{}?period={}&limit=400&apikey={}"
            return template.format(self.ticker, self.period, api_key)
        elif data_type == 'metrics':
            template = "https://financialmodelingprep.com/api/v3/"\
                            "key-metrics/{}?period={}&limit=400&apikey={}"
            
            return template.format(self.ticker, self.period, api_key)
        elif data_type == 'info':
            template = "https://financialmodelingprep.com/api/v3/"\
                        "profile/{}?apikey={}"
            return template.format(self.ticker, api_key)
        else:
            template = "https://financialmodelingprep.com/api/v3/"\
                        "income-statement/{}?period={}&limit=400&apikey={}"
            return template.format(self.ticker, self.period, api_key)
    
    @staticmethod
    def make_fmp_api_requests(url: str) -> Response:
        fmp_response = requests.get(url)
        assert fmp_response.status_code == 200, 'Request unsuccessful'
        return fmp_response

    @staticmethod
    def convert_raw_data_to_json(response: Response) -> json:
        return response.json()