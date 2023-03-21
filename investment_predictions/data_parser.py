### TODO: Do some data validation: column dtypes, ensure all cells are numeric etc
### TODO: Create the dataset builder class based on tickers from fmp


import pandas as pd
from typing import Dict, List, Tuple
import json
from pathlib import Path
import datetime as dt
import numpy as np

feature_path = Path.cwd() / "investment_predictions" / "features.json"
with open(feature_path, "r") as f:
    features = json.load(f)


class DataParser:
    """
    This class is built to accept the DataScraper.data_dictionary dictionary, parse the 
    data and create a single DataFrame that represents the data for that company. 

    The dictionary passed as an argument contains data relevant to a single company, 
    and thus the returned DataFrame is specific to that single company. The current 
    DataScraper design should only be used with "company" as the data_type argument,
    and thus the only acceptable keys in the DataScraper.data_dictionary are 'info', 
    'metrics', 'ratios', 'is', and 'price'. When parsed, only relevant data is 
    passed back from each of the sub-dictionaries. The relevant data is defined in 
    the local features.json file that should be present in the same directory as 
    this data_parser.py file. Duplicate features are not returned e.g.: 
    self.parse_metrics() does not return features that are already returned from 
    self.parse_ratios().

    Args:
        data_dictionary (Dict[str, List]): A dictionary containing data relevant to a 
            single company.

    Attributes:
        data_dictionary (Dict[str, List]): A dictionary containing data relevant 
            to a single company.
        info (pd.DataFrame): A DataFrame containing company information such as 
            symbol, companyName, currency, exchange, industry, and sector.
        ratios (pd.DataFrame): A DataFrame containing relevant data from the 
            ratios sub-dictionary.
        metrics (pd.DataFrame): A DataFrame containing relevant data from the 
            metrics sub-dictionary.
        is_ (pd.DataFrame): A DataFrame containing relevant data from the is 
            sub-dictionary.
        price (pd.DataFrame): A DataFrame containing daily price data for the 
            company, filtered into quarters.
        snp_500 (pd.DataFrame): A DataFrame containing daily price data for the 
            S&P500 index, filtered into quarters.
        final_data (pd.DataFrame): A DataFrame containing all the relevant data 
            from info, ratios, metrics, is_, price, and snp_500 DataFrames combined.
        returns (pd.DataFrame): A DataFrame containing calculated relative returns.

    Methods:
        json_to_dataframe(json_data: Dict[str, List]) -> pd.DataFrame:
            Converts JSON data to a pandas DataFrame.
        
        create_df_index(df: pd.DataFrame) -> pd.Index:
            Creates a pandas Index for the given DataFrame.
        
        create_period_start_date_feature(date_string_array: np.array) -> List[str]:
            Creates a start_date feature for the given date string array.
        
        parse_data_dictionary():
            Parses the data dictionary.
        
        parse_info() -> pd.DataFrame:
            Parses the info sub-dictionary to return a DataFrame with relevant 
            company information.
        
        parse_ratios() -> pd.DataFrame:
            Parses the ratios sub-dictionary to return a DataFrame with relevant 
            data and period_start_date.
        
        parse_metrics() -> pd.DataFrame:
            Parses the metrics sub-dictionary to return a DataFrame with relevant
            data and period_start_date.
        
        parse_income_statement() -> pd.DataFrame:
            Parses the is sub-dictionary to return a DataFrame with relevant data 
            and period_start_date.
        
        parse_price() -> pd.DataFrame:
            Parses the price sub-dictionary to return a DataFrame containing daily 
            price data for the company.
        
        filter_dataframes() -> None:
            Filters all DataFrames to include only common indices.
        
        load_snp_500() -> pd.DataFrame:
            Loads and returns daily price data for the S&P500 index.
        
        filter_daily_into_quarters(df: pd.DataFrame, tag: str='stock') -> pd.DataFrame:
        Filters the given DataFrame containing daily price data into quarters 
        and returns a new DataFrame with stock price averages, highs, and lows 
        for each quarter.
    
        create_date_objects_from_strings(date_string_array: np.array) -> np.array:
            Converts the given date string array to an array of date objects.
        
        create_date_objects_from_pd_timestamps(timestamp_array) -> np.array:
            Converts the given pandas timestamp array to an array of date objects.
        
        calculate_PE_ratios() -> None:
            Calculates PE ratios for the company and updates the ratios DataFrame.
        
        combine_dataframes() -> pd.DataFrame:
            Combines info, ratios, metrics, is, price, and snp_500 DataFrames into a 
            single DataFrame.
        
        calculate_internal_returns() -> List:
            Calculates returns for the company's stock price and the S&P 500 index,
            with a lag of 1, 2, 3, or 4 quarters, and stores them in the respective
            DataFrames.
        
        calculate_relative_returns() -> pd.DataFrame:
            Calculates the returns of the company's stock price relative to the 
            S&P 500 index returns, with a lag of 1, 2, 3, or 4 quarters, and 
            returns a DataFrame containing these values.

    """

    def __init__(self, data_dictionary: Dict[str, List]):
        """
        Initializes a new instance of the DataParser class.

        Args:
            data_dictionary (Dict[str, List]): A dictionary containing data 
            relevant to a single company.

        Returns:
            None
        """
        self.data_dictionary = data_dictionary
        self.info = self.pasrse_data_dictionary('info')
        self.ratios = self.pasrse_data_dictionary('ratios')
        self.metrics = self.pasrse_data_dictionary('metrics')
        self.is_ = self.pasrse_data_dictionary('is')
        self.price = self.filter_daily_into_quarters(self.pasrse_data_dictionary('price'))
        self.snp_500 = self.filter_daily_into_quarters(self.load_snp_500(), "S&P500")
        self.filter_dataframes()
        self.calculate_PE_ratios()
        self.calculate_internal_returns()
        self.returns = self.calculate_relative_returns()
        self.final_data = self.combine_dataframes()


    @staticmethod
    def json_to_dataframe(json_data: Dict[str, List]) -> pd.DataFrame:
        """
        Converts JSON data to a pandas DataFrame.

        Args:
            json_data (Dict[str, List]): A dictionary containing the JSON data to 
            be converted.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the converted data.
        """
        return pd.DataFrame(json_data)

    def create_df_index(self, df: pd.DataFrame) -> pd.Index:
        """
        Creates a pandas Index for the given DataFrame.

        Args:
            df (pd.DataFrame): A pandas DataFrame to create the index for.

        Returns:
            pd.Index: A pandas Index object.
        """
        ticker = self.info["symbol"][0]
        periods = df.period
        years = df.date.apply(lambda x: x.split("-")[0])
        index = ticker + "-" + periods + "-" + years
        return pd.Index(index)

    @staticmethod
    def create_period_start_date_feature(date_string_array) -> List[str]:
        """
        Creates a list of start dates for a given array of date strings.

        Args:
            date_string_array (Iterable[str]): An iterable of date strings in 
            'YYYY-MM-DD' format.

        Returns:
            List[str]: A list of start dates, represented as strings in 
            'YYYY-MM-DD' format.
        """
        dates = np.array(
            [dt.date(*[int(i) for i in date.split("-")]) for date in date_string_array]
        )
        start_dates = dates - dt.timedelta(91)
        return [str(date) for date in start_dates]

    def pasrse_data_dictionary(self, key: str):
        """
        Parse data from the data dictionary based on a given key and return a DataFrame with
        the relevant columns.

        Args:
            key (str): The key of the data to be parsed from the data dictionary.

        Returns:
            pd.DataFrame: A DataFrame with the relevant columns for the given key.

        Raises:
            AssertionError: If the key is not in the data dictionary.
        """
        assert key in self.data_dictionary.keys(), "invalid key"
        json_data = self.data_dictionary[key]
        df_data = self.json_to_dataframe(json_data)
        cols = features[key]
        
        if key in ['ratios', 'metrics', 'is']:
            df_data["start_date"] = \
                self.create_period_start_date_feature(df_data.date)
            df_data.index = self.create_df_index(df_data)
            extra_cols = ['start_date']
        elif key == 'price':
            df_data["date"] = self.create_date_objects_from_pd_timestamps(df_data.index)
            extra_cols = ['date']
        else:
            extra_cols = []

        return df_data[cols+extra_cols]

    def filter_dataframes(self) -> None:
        """
        Filters the instance's DataFrames to only include common indices.

        Returns:
            None
        """
        common_idx = self.ratios.index
        common_idx = common_idx.intersection(self.metrics.index)
        common_idx = common_idx.intersection(self.is_.index)
        common_idx = common_idx.intersection(self.price.index)
        self.ratios = self.ratios.loc[common_idx]
        self.metrics = self.metrics.loc[common_idx]
        self.is_ = self.is_.loc[common_idx]
        self.price = self.price.loc[common_idx]
        self.snp_500 = self.snp_500.loc[common_idx]
        failed_msg = "Dataframe filtering failed"
        assert self.ratios.index.equals(self.metrics.index), failed_msg
        assert self.ratios.index.equals(self.is_.index), failed_msg
        assert self.ratios.index.equals(self.price.index), failed_msg
        assert self.ratios.index.equals(self.snp_500.index), failed_msg

    def load_snp_500(self):
        """
        Loads the S&P 500 trading data from a parquet file.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the S&P 500 trading data.
        """
        path = (
            Path.cwd()
            / "investment_predictions"
            / "data"
            / "snp500_trading_data_1970_to_2023.parquet"
        )
        df = pd.read_parquet(path)
        df["date"] = self.create_date_objects_from_pd_timestamps(df.index)
        return df

    def filter_daily_into_quarters(self, df: pd.DataFrame, tag: str = "stock") -> None:
        """
        Filters daily stock data into quarterly data.

        Args:
            df (pd.DataFrame): A pandas DataFrame containing daily stock data.
            tag (str): A string representing the type of stock data being filtered 
                (default 'stock').

        Returns:
            pd.DataFrame: A pandas DataFrame containing quarterly stock data.
        """
        start_date_objects = self.create_date_objects_from_strings(
            self.ratios.start_date
        )
        end_date_objects = self.create_date_objects_from_strings(self.ratios.date)
        working_index = self.ratios.index

        filtered_data = []
        filtered_index = []
        for start, end, idx in zip(start_date_objects, end_date_objects, working_index):
            try:
                period_price = df[(df.date >= start) & (df.date < end)]
                max_ = max(period_price["High"])
                min_ = min(period_price["Low"])
                close = period_price["Close"].mean()
                filtered_data.append([close, max_, min_])
                filtered_index.append(idx)
            except ValueError:
                continue

        new_df = pd.DataFrame(
            filtered_data,
            columns=[f"{tag}PriceAverage", f"{tag}PriceHigh", f"{tag}PriceLow"],
            index=filtered_index,
        )
        return new_df

    @staticmethod
    def create_date_objects_from_strings(date_string_array: np.array) -> np.array:
        """
        Creates an array of date objects from an array of date strings.

        Args:
            date_string_array (np.array): A NumPy array of date strings in the format 
            'YYYY-MM-DD'.

        Returns:
            np.array: A NumPy array of date objects.
        """
        return np.array(
            [dt.date(*[int(i) for i in date.split("-")]) for date in date_string_array]
        )

    @staticmethod
    def create_date_objects_from_pd_timestamps(timestamp_array) -> np.array:
        """
        Creates an array of date objects from an array of pandas Timestamps.

        Args:
            timestamp_array (np.array): A NumPy array of pandas Timestamps.

        Returns:
            np.array: A NumPy array of date objects.
        """
        return np.array(
            [
                dt.date(*[int(i) for i in str(stamp).split()[0].split("-")])
                for stamp in timestamp_array
            ]
        )

    def calculate_PE_ratios(self) -> None:
        """
        Calculates the PE ratios of the company and adds them as columns to the ratios 
        DataFrame.

        The PE ratios are calculated as the average, low, and high prices divided by 
        four times the EPS.

        Returns:
            None.
        """
        eps = self.is_.eps
        self.ratios["PE_avg"] = self.price["stockPriceAverage"] / (4 * eps)
        self.ratios["PE_low"] = self.price["stockPriceLow"] / (4 * eps)
        self.ratios["PE_high"] = self.price["stockPriceHigh"] / (4 * eps)

    def combine_dataframes(self) -> pd.DataFrame:
        """
        Combines the parsed and filtered DataFrames for the company into a single 
        DataFrame.

        The method drops the 'date' and 'period' columns from the metrics and income 
        statement DataFrames, joins all DataFrames on their common index, and returns 
        the resulting DataFrame.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the combined data for the 
            company.
        """
        to_drop = ["date", "period"]
        self.metrics = self.metrics.drop(to_drop, axis=1)
        self.is_ = self.is_.drop(to_drop, axis=1)
        to_join = [self.ratios, 
                   self.metrics, 
                   self.is_, 
                   self.price, 
                   self.snp_500,
                   self.returns]
        return pd.concat(to_join, axis=1)

    def calculate_returns_from_series(self, price: pd.DataFrame, interval: int=1) -> List:
        """
        Calculate the returns for the given price DataFrame over a specified interval.
        Assumes that the most recent price is at the top of the df.

        Args:
            price (pd.DataFrame): DataFrame containing the historical prices.
            interval (int, optional): The number of time intervals to calculate returns over.
                Defaults to 1.

        Returns:
            List: A list of returns calculated for the given interval, with NaN values at the end.

        Raises:
            TypeError: If price is not a pandas DataFrame.
            ValueError: If interval is less than 1.
        """
        interval = int(interval)
        price_series = list(reversed(price))
        returns = []
        for idx, price in enumerate(price_series[: -interval]):
            returns.append(price_series[idx+interval]/price)
        for _ in range(interval):
            returns.append(np.nan)
        return list(reversed(returns))
    
    def calculate_internal_returns(self) -> List:
        """Calculates internal returns over 1, 2, 3, and 4 quarters by calculating 
        the ratio of the average stock prices for those quarters. 
        
        Returns:
            None
        """
        for i in [1, 2, 3, 4]:
            self.price[f'stockPriceRatio_{i}Q'] = self.calculate_returns_from_series(
                self.price['stockPriceAverage'], i
            )
            self.snp_500[f'snpPriceRatio_{i}Q'] = self.calculate_returns_from_series(
                self.snp_500['S&P500PriceAverage'], i
            )
            
    def calculate_relative_returns(self):
        """Calculates the relative returns of the stock compared to the S&P500 
            over 1Q, 2Q, 3Q, and 4Q periods.
    
        Returns:
            relative_returns_df: pd.DataFrame
                A DataFrame containing the relative returns of the stock compared 
                to the S&P 500 over 1Q, 2Q, 3Q, and 4Q periods.
        """
        relative_returns_df = pd.DataFrame(index=self.ratios.index)
        for i in [1, 2, 3, 4]:
            header = f"priceRatioRelativeToS&P_{i}Q"
            stock_return = self.price[f'stockPriceRatio_{i}Q']
            snp_return = self.snp_500[f'snpPriceRatio_{i}Q']
            relative_return = stock_return/snp_return
            relative_returns_df[header] = relative_return
        return relative_returns_df


