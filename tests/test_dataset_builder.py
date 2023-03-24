import sys
from investment_predictions import DataScraper, DataParser, DatasetBuilder
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

feature_path = Path.cwd() / "investment_predictions" / "features.json"
with open(feature_path, "r") as f:
    features = json.load(f)

def generate_class_instance():
    return DatasetBuilder(['New York Stock Exchange'])

class TestDatasetBuilder(unittest.TestCase):

    def test_get_fmp_api_url(self):
        instance = DatasetBuilder(['New York Stock Exchange'])
        expected = f'https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}'
        result = instance.get_fmp_api_url()
        self.assertEqual(result, expected)
        self.assertNotEqual(expected, 'test')

    def test_make_stock_ticker_api_request(self):
        url = "fakeurl.com"
        response = Mock()
        response.status_code = 200
        instance = generate_class_instance()
        with patch("requests.get", return_value=response) as mock_method:
            result = instance.make_stock_ticker_api_request(url)
            self.assertEqual(result, response)
            mock_method.assert_called_once_with(url)
            response.status_code = 100
            with self.assertRaises(AssertionError):
                instance.make_stock_ticker_api_request(url)

    def test_fetch_raw_stock_ticker_data(self):
        pass

    def test_set_exchanges(self):
        pass

    def test_build_dataset(self):
        pass

    def test_data_validation(self):
        pass

    
