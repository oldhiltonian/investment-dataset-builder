import sys
from investment_predictions import DataScraper, DataParser
import unittest
from unittest.mock import Mock, patch
import itertools
from pathlib import Path
import requests
import pandas as pd
import datetime as dt


sys.path.append("..")

key_path = Path().home() / "desktop" / "FinancialModellingPrep_API.txt"
with open(key_path) as file:
    api_key = file.read()


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
                

