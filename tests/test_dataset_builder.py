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


class TestDatasetBuilder(unittest.TestCase):

    def test_get_fmp_api_url(self):
        instance = DatasetBuilder(['New York Stock Exchange'])
        expected = f'https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}'
        result = instance.get_fmp_api_url()
        self.assertEqual(result, expected)
        self.assertNotEqual(expected, 'test')
