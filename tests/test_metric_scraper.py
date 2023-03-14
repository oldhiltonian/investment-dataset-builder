from investment_predictions import DataScraper
import unittest
from unittest.mock import Mock, patch
import itertools
from pathlib import Path
import requests

import sys
sys.path.append('..')

key_path = Path().home() / "desktop" / "FinancialModellingPrep_API.txt"
with open(key_path) as file:
    api_key = file.read()



def instance_generator():
    tickers = ['AAPL', 'NVDA', 'MSFT', 'JXN']
    periods = ['annual', 'quarter']
    for ticker, period in itertools.product(tickers, periods):
        yield DataScraper(ticker, period)
    


class TestMetricScraper(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_multi_line_string_stripper(self):
        pass

    def test_get_fmp_api_url(self):
        for instance in instance_generator():
            ticker = instance.ticker
            period = instance.period
            for string in instance.fmp_api_requests:
                if string == 'ratios':
                    template = "https://financialmodelingprep.com/api/"\
                                "v3/ratios/{}?period={}&limit=400&apikey={}"
                    expected = template.format(ticker, period, api_key)
                elif string == 'metrics':
                    template = "https://financialmodelingprep.com/api/v3/"\
                                    "key-metrics/{}?period={}&limit=400&apikey={}"
                    
                    expected= template.format(ticker, period, api_key)
                elif string == 'info':
                    template = "https://financialmodelingprep.com/api/v3/"\
                                "profile/{}?apikey={}"
                    expected = template.format(ticker, api_key)
                else:
                    template = "https://financialmodelingprep.com/api/v3/"\
                                "income-statement/{}?period={}&limit=400&apikey={}"
                    expected = template.format(ticker, period, api_key)

                result = instance.get_fmp_api_url(string)
                self.assertEqual(result, expected)

    def test_make_fmp_api_request(self):
        for instance in instance_generator():
            mock_response = Mock(spec=requests.models.Response)
            mock_response.status_code = 200
            mock_response.content = b'{"result": "success"}'

            with patch('requests.get', return_value=mock_response):
                url = "https://example.com/api"
                response = instance.make_fmp_api_requests(url)
                self.assertEqual(response.status_code, 200)

    def test_convert_raw_data_to_json(self):
        for instance in instance_generator():
            mock_response = Mock(spec=requests.models.Response)
            mock_response.content = b'{"result": "success"}'
            mock_response.json.return_value = {"result": "success"}
            expected = {"result": "success"}
            result = instance.convert_raw_data_to_json(mock_response)
            self.assertEqual(result, expected)