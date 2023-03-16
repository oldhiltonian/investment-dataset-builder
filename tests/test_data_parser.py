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
        for instance in parser_instance_generator():
            instance.info['symbol'][0] = 'TEST'
            test_df = pd.DataFrame([['Q1', '2000-01-12'],
                                   ['Q4', '1995-11-10'],
                                   ['Q3', '2020-07-28']],
                                   columns=['period', 'date'])
            expected_index = pd.Index(['TEST-Q1-2000', 'TEST-Q4-1995', 'TEST-Q3-2020'])
            result_index = instance.create_df_index(test_df)
            self.assertEqual(result_index.equals(expected_index), True)

    def test_create_period_start_date_feature(self):
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

    def test_filter_dataframes(self):
        for instance in parser_instance_generator():
            # Setting the dataframes to predetermined values
            instance.ratios = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6], 'C': [7,8,9]})
            instance.ratios.index = pd.Index(['X', 'Y', 'Z'])
            instance.metrics = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6], 'C': [7,8,9]})
            instance.metrics.index = pd.Index(['J', 'Z', 'N'])
            instance.is_ = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6], 'C': [7,8,9]})
            instance.is_.index = pd.Index(['Z', 'G', 'F'])
            instance.price = pd.DataFrame({'A': [1,2,3], 'B': [4,5,6], 'C': [7,8,9]})
            instance.price.index = pd.Index(['Z', 'v', 'w'])
            
            # The expected dataframes after filering are as follows
            expected_ratios = pd.DataFrame({'A':3, 'B': 6, 'C': 9}, index=['Z'])
            expected_metrics = pd.DataFrame({'A':2, 'B': 5, 'C': 8}, index=['Z'])
            expected_is_ = pd.DataFrame({'A':1, 'B': 4, 'C': 7}, index=['Z'])
            expected_price = pd.DataFrame({'A': 1, 'B': 4, 'C': 7}, index=['Z'])

            # Filter then check
            instance.filter_dataframes()
            self.assertEqual(expected_ratios.equals(instance.ratios), True)
            self.assertEqual(expected_metrics.equals(instance.metrics), True)
            self.assertEqual(expected_is_.equals(instance.is_), True)
            self.assertEqual(expected_price.equals(instance.price), True)
    

    def test_filter_price_into_periods(self):
        pass

    def test_create_date_objects_from_strings(self):
        date_string_array = ['2000-01-01', '2020-10-12', "2023-01-19", "2019-07-12"]
        expected = [dt.date(2000, 1, 1), dt.date(2020, 10, 12), dt.date(2023, 1, 19),
                    dt.date(2019, 7, 12)]
        for instance in parser_instance_generator():
            result = list(instance.create_date_objects_from_strings(date_string_array))
            self.assertEqual(result, expected)

    def test_create_date_objects_from_pd_timestamps(self):
        from pandas._libs.tslibs.timestamps import Timestamp as ts
        date_string_array = ['2000-01-01', '2020-10-12', "2023-01-19", "2019-07-12"]
        timestamp_array = [ts(i) for i in date_string_array]
        expected = [dt.date(2000, 1, 1), dt.date(2020, 10, 12), dt.date(2023, 1, 19),
                    dt.date(2019, 7, 12)]
        for instance in parser_instance_generator():
            result = list(instance.create_date_objects_from_pd_timestamps(timestamp_array))
            self.assertEqual(result, expected)


