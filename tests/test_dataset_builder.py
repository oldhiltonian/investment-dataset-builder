import sys
from investment_dataset_builder import DataScraper, DataParser, DatasetBuilder
import unittest
from unittest.mock import Mock, patch
import itertools
from pathlib import Path
import requests
import pandas as pd
import datetime as dt
import numpy as np
import json

sys.path.append("..")

key_path = Path().home() / "desktop" / "FinancialModellingPrep_API.txt"
with open(key_path) as file:
    api_key = file.read()

feature_path = Path.cwd() / "investment_dataset_builder" / "features.json"
with open(feature_path, "r") as f:
    features = json.load(f)


def generate_class_instance():
    return DatasetBuilder(["New York Stock Exchange"])


class TestDatasetBuilder(unittest.TestCase):
    def test_get_fmp_api_url(self):
        instance = DatasetBuilder(["New York Stock Exchange"])
        expected = (
            f"https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}"
        )
        result = instance.get_fmp_api_url()
        self.assertEqual(result, expected)
        self.assertNotEqual(expected, "test")

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

    def test_response_to_json(self):
        toy_dict = {"symbol": "AAPL", "Name": "Apple Inc"}
        instance = DatasetBuilder()
        response = Mock()
        response.json = Mock(return_value=toy_dict)
        result = instance.response_to_json(response)
        self.assertEqual(result, toy_dict)
        response.json.assert_called_once()

    def test_fetch_raw_stock_ticker_data(self):
        """This function is not tested explicitly as it is a composition#
            of three other functions which are all unittested above"""

    def test_set_exchanges(self):
        instance = DatasetBuilder()
        exchange_list = [
            ["AMEX", "BSE", "Athens"],
            ["Fukuoka", "KOSDAQ", "Lisbon"],
            ["NASDAQ", "NSE", "Prague"],
        ]
        for exchanges in exchange_list:
            instance.set_exchanges(exchanges)
            self.assertEqual(exchanges, instance.exchanges)

        for item in [np.nan, "", "abc"]:
            with self.assertRaises(AssertionError):
                instance.set_exchanges([item])

    def test_is_valid_security(self):
        instance = generate_class_instance()
        instance.set_exchanges(["Helsinki", "Iceland", "Milan", "NSE"])
        good_dicts = [
            {"type": "stock", "exchange": "Helsinki"},
            {"type": "stock", "exchange": "Iceland"},
            {"type": "stock", "exchange": "Milan"},
            {"type": "stock", "exchange": "NSE"},
        ]
        bad_dicts = [
            {"type": "notstock", "exchange": "Helsinki"},
            {"type": "", "exchange": "Iceland"},
            {"type": "STOCK", "exchange": "Milan"},
            {"type": "Stock", "exchange": "NSE"},
            {"type": "stock", "exchange": "Helsink"},
            {"type": "stock", "exchange": "Icelnd"},
            {"type": "stock", "exchange": "Mian"},
            {"type": "stock", "exchange": "NS"},
        ]

        for dct in good_dicts:
            result = instance.check_valid_security(dct)
            self.assertEqual(result, True)

        for dct in bad_dicts:
            result = instance.check_valid_security(dct)
            self.assertEqual(result, False)

    def test_build_dataset(self):
        "Need to build this"
        pass
