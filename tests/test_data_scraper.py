import sys
from investment_predictions import DataScraper
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


def scraper_instance_generator():
    """
    Generator function that yields instances of the DataScraper class for various tickers and periods.

    Yields:
        DataScraper: An instance of the DataScraper class.

    """
    tickers = ["AAPL", "NVDA", "MSFT", "JXN"]
    periods = ["annual", "quarter"]
    data_types = ["company", "economic"]
    for ticker, period, data_type in itertools.product(tickers, periods, data_types):
        yield DataScraper(ticker, api_key, period, data_type)


class TestDataScraper(unittest.TestCase):
    """
    A unittest test case for the DataScraper class.

    """

    def test_assert_valid_user_inputs(self):
        """
        Test for the assert_valid_user_inputs method of the DataScraper class.

        Raises:
            AssertionError: Raised if the ticker is not uppercase, if the period is not lowercase and not equal to 'annual' or 'quarter',
            or if the api_key is empty.
        """
        for instance in scraper_instance_generator():
            instance.assert_valid_user_inputs()
            for i in range(10):
                if i % 2 == 0:
                    instance.ticker = "lol"
                elif i % 3 == 0:
                    instance.period = "OI"
                else:
                    instance.api_key = ""
                with self.assertRaises(AssertionError):
                    instance.assert_valid_user_inputs()

    def test_get_fmp_api_url(self):
        """
        Test for the get_fmp_api_url method of the DataScraper class.

        Raises:
            AssertionError: Raised if the result of get_fmp_api_url does not match the expected URL.

        """
        for instance in scraper_instance_generator():
            ticker = instance.ticker
            period = instance.period
            dtype = instance.data_type
            end_date = str(dt.date.today())
            if dtype == "company":
                request_list = instance.fmp_company_requests
            else:
                request_list = instance.fmp_economic_requests
            for string in request_list:
                if string == "ratios":
                    template = (
                        "https://financialmodelingprep.com/api/"
                        "v3/ratios/{}?period={}&limit=400&apikey={}"
                    )
                    expected = template.format(ticker, period, api_key)
                elif string == "metrics":
                    template = (
                        "https://financialmodelingprep.com/api/v3/"
                        "key-metrics/{}?period={}&limit=400&apikey={}"
                    )

                    expected = template.format(ticker, period, api_key)
                elif string == "info":
                    template = (
                        "https://financialmodelingprep.com/api/v3/"
                        "profile/{}?apikey={}"
                    )
                    expected = template.format(ticker, api_key)
                elif string == "is":
                    template = (
                        "https://financialmodelingprep.com/api/v3/"
                        "income-statement/{}?period={}&limit=400&apikey={}"
                    )
                    expected = template.format(ticker, period, api_key)
                elif string == "TYield":
                    template = (
                        "https://financialmodelingprep.com/api/v4/"
                        "treasury?from=1970-06-30&to={}&apikey={}"
                    )
                    expected = template.format(end_date, api_key)
                elif string in ["realGDPPerCapita", "CPI", "consumerSentiment"]:
                    template = (
                        "https://financialmodelingprep.com/api/v4/"
                        "economic?name={}&from=1970-06-30&to={}&apikey={}"
                    )
                    expected = template.format(string, end_date, api_key)
                result = instance.get_fmp_api_url(string)
                self.assertEqual(result, expected)

    def test_make_fmp_api_request(self):
        """
        Test for the make_fmp_api_request method of the DataScraper class.

        Raises:
            AssertionError: Raised if the response status code is not 200.

        """
        for instance in scraper_instance_generator():
            mock_response = Mock(spec=requests.models.Response)
            mock_response.status_code = 200
            mock_response.content = b'{"result": "success"}'

            with patch("requests.get", return_value=mock_response):
                url = "https://example.com/api"
                response = instance.make_fmp_api_requests(url)
                self.assertEqual(response.status_code, 200)

    def test_convert_raw_data_to_json(self):
        """
        Test for the convert_raw_data_to_json method of the DataScraper class.

        Raises:
            AssertionError: Raised if the result of convert_raw_data_to_json does not match the expected result.

        """
        for instance in scraper_instance_generator():
            mock_response = Mock(spec=requests.models.Response)
            mock_response.content = b'{"result": "success"}'
            mock_response.json.return_value = {"result": "success"}
            expected = {"result": "success"}
            result = instance.convert_raw_data_to_json(mock_response)
            self.assertEqual(result, expected)

    def test_fetch_stock_price_data(self):
        """
        Test for the fetch_stock_price_data method of the DataScraper class.

        Raises:
            AssertionError: Raised if there is insufficient stock price data, if the columns of the DataFrame do not match the expected columns,
            or if the returned object is not a pandas DataFrame.

        """
        for instance in scraper_instance_generator():
            data = instance.fetch_stock_price_data()
            self.assertGreater(len(data), 85)
            cols = data.columns
            expected_cols = pd.Index(
                ["Open", "High", "Low", "Close", "Adj Close", "Volume"], dtype="object"
            )
            self.assertEqual(cols.equals(expected_cols), True)
            self.assertIsInstance(data, pd.DataFrame)

    def test_fetch_data(self):
        """
        Test for the fetch_data method of the DataScraper class.

        Raises:
            AssertionError: Raised if the length of the returned dictionary is not correct,
            if a key in the returned dictionary is not a string, or
            if the value of a key in the returned dictionary is not a list.

        """
        for instance in scraper_instance_generator():
            data = instance.data_dictionary
            if instance.data_type == "company":
                expected_length = len(instance.fmp_company_requests) + 1
            elif instance.data_type == "economic":
                expected_length = len(instance.fmp_economic_requests) + 1
            self.assertEqual(len(data), expected_length)
            for key in data.keys():
                self.assertIsInstance(key, str)
                if key != 'price':
                    self.assertIsInstance(data[key], list)
                else:
                    self.assertIsInstance(data[key], pd.DataFrame)
