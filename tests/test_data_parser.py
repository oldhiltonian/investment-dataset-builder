import sys
from investment_predictions import DataScraper, DataParser
import unittest
from unittest.mock import Mock, patch
import itertools
from pathlib import Path
import requests
import pandas as pd
import datetime as dt
import json


sys.path.append("..")

key_path = Path().home() / "desktop" / "FinancialModellingPrep_API.txt"
with open(key_path) as file:
    api_key = file.read()

feature_path = Path.cwd()/'investment_predictions'/'features.json'
with open(feature_path, 'r') as f:
    features = json.load(f)

def parser_instance_generator():
    """
    Generator function that yields instances of the DataScraper class for various tickers and periods.

    Yields:
        DataScraper: An instance of the DataScraper class.

    """
    tickers = ["AAPL", "NVDA", "MSFT", "JXN"]
    periods = ["annual", "quarter"]
    data_types = ["company"]
    for ticker, period, data_type in itertools.product(tickers, periods, data_types):
        d = DataScraper(ticker, api_key, period, data_type).data_dictionary
        yield DataParser(d)

class TestDataParser(unittest.TestCase):

    def test_json_to_dataframe(self):
        for instance in parser_instance_generator():
            d = instance.data_dictionary
            for key in ['info', 'ratios', 'metrics', 'is']:
                data = d.get(key)
                expected = pd.DataFrame(d[key])
                result = instance.json_to_dataframe(d[key])
                self.assertEqual(expected.equals(result), True)

    def test_create_df_index(self):
        pass

    def test_parse_info(self):
        for instance in parser_instance_generator():
            instance.data_dictionary['info'] = [{'symbol': 'AAPL',
                                                'changes': 0.4,
                                                'companyName': 'Apple Inc.',
                                                'currency': 'USD',
                                                'cik': '0000320193',
                                                'isin': 'US0378331005',
                                                'cusip': '037833100',
                                                'exchange': 'NASDAQ Global Select',
                                                'exchangeShortName': 'NASDAQ',
                                                'industry': 'Consumer Electronics',
                                                'sector': 'Technology',
                                                'country': 'US',
                                                'isActivelyTrading': True,}
                                                ]
            expected = pd.DataFrame ([{'symbol': 'AAPL',
                            'companyName': 'Apple Inc.',
                            'currency': 'USD',
                            'exchange': 'NASDAQ Global Select',
                            'industry': 'Consumer Electronics',
                            'sector': 'Technology',}
                            ])
            result = instance.parse_info()
            self.assertEqual(expected.equals(result), True)

    def test_parse_ratios(self):
        '''Currently just asserts that the columns and data shapes are correct'''
        for instance in parser_instance_generator():
            result_df = instance.parse_ratios()
            result_cols = result_df.columns.to_list()
            expected_cols = features['ratios']
            self.assertEqual(result_cols, expected_cols)
            self.assertEqual(len(result_df), len(instance.data_dictionary['ratios']))
                

    def test_parse_metrics(self):
        '''Currently just asserts that the columns and data shapes are correct'''
        for instance in parser_instance_generator():
            result_df = instance.parse_metrics()
            result_cols = result_df.columns.to_list()
            expected_cols = features['metrics']
            self.assertEqual(result_cols, expected_cols)
            self.assertEqual(len(result_df), len(instance.data_dictionary['metrics']))

    def test_parse_income_statement(self):
        '''Currently just asserts that the columns and data shapes are correct'''
        for instance in parser_instance_generator():
            result_df = instance.parse_income_statement()
            result_cols = result_df.columns.to_list()
            expected_cols = features['is']
            self.assertEqual(result_cols, expected_cols)
            self.assertEqual(len(result_df), len(instance.data_dictionary['is']))

    def test_parse_price(self):
        for instance in parser_instance_generator():
            df = instance.parse_price()
            expected_cols = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
            result_cols = df.columns.to_list()
            self.assertEqual(result_cols, expected_cols)
            self.assertGreater(len(df), 84)
