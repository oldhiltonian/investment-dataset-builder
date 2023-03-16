import pandas as pd
from typing import Dict, List, Tuple
import json
from pathlib import Path 
import datetime as dt
import numpy as np

feature_path = Path.cwd()/'investment_predictions'/'features.json'
with open(feature_path, 'r') as f:
    features = json.load(f)

class DataParser:
    """
    This class is built to accept the DataScraper.data_dictionary ditionary, parse the 
    data and return a single DataFrame that represents the data for that company. 

    The dictionary passed as an argument contains data relevant to a single company, and thus
    the returned DataFrame is specific to that single company. The current DataScraper design
    should only be used with "company" as the data_type argument, and thus the only acceptable
    keys in the DataScraper.data_dictionary are 'info', 'metrics', 'ratios', 'is' and, 'price'.
    When parsed, only relevant data is passed back from each of the sub-dictionaries. The
    relevant data is defined in the local features.json file that should be present in the
    same directory as this data_parser.py file. Duplicate features are not retured e.g. 
    self.parse_metrics() does not return features that are already returned from 
    self.parse_ratios().

    """

    def __init__(self, data_dictionary: Dict[str, List]):
        self.data_dictionary = data_dictionary
        self.info = self.parse_info()
        self.ratios = self.parse_ratios()
        self.metrics = self.parse_metrics()
        self.is_ = self.parse_income_statement()
        self.filter_dataframes()
        self.price = self.parse_price()

    @staticmethod
    def json_to_dataframe(json_data: Dict[str, List]) -> pd.DataFrame:
        return pd.DataFrame(json_data)
    
    def create_df_index(self, df):
        ticker = self.info['symbol'][0]
        periods = df.period
        years = df.date.apply(lambda x: x.split('-')[0])
        index = ticker+'-'+periods+'-'+years
        return pd.Index(index)
    
    @staticmethod
    def create_period_start_date_feature(date_array):
        dates = np.array([dt.date(*[int(i) for i in date.split('-')]) for date in date_array])
        start_dates = dates - dt.timedelta(91)
        return [str(date) for date in start_dates]
        

    def pasrse_data_dictionary(self):
        pass

    def parse_info(self) -> pd.DataFrame:
        json_data = self.data_dictionary['info']
        cols = ['symbol', 'companyName', 'currency', 'exchange', 'industry', 'sector']
        df_data = self.json_to_dataframe(json_data)
        return df_data[cols]
    
    def parse_ratios(self) -> pd.DataFrame:
        '''Need to create period_start_date column as date-91 days'''
        cols = features['ratios']+['start_date']
        json_data = self.data_dictionary['ratios']
        df_data = self.json_to_dataframe(json_data)
        df_data['start_date'] = self.create_period_start_date_feature(df_data.date)
        df_data.index = self.create_df_index(df_data)
        return df_data[cols]
    
    def parse_metrics(self) -> pd.DataFrame:
        cols = features['metrics']+['start_date']
        json_data = self.data_dictionary['metrics']
        df_data = self.json_to_dataframe(json_data)
        df_data['start_date'] = self.create_period_start_date_feature(df_data.date)
        df_data.index = self.create_df_index(df_data)
        return df_data[cols]

    def parse_income_statement(self) -> pd.DataFrame:
        cols = features['is']+['start_date']
        json_data = self.data_dictionary['is']
        df_data = self.json_to_dataframe(json_data)
        df_data['start_date'] = self.create_period_start_date_feature(df_data.date)
        df_data.index = self.create_df_index(df_data)
        return df_data[cols]

    def parse_price(self) -> pd.DataFrame:
        return self.data_dictionary['price'][0]
    
    def filter_dataframes(self):
        common_idx = self.ratios.index
        common_idx = common_idx.intersection(self.metrics.index)
        common_idx = common_idx.intersection(self.is_.index)
        self.ratios = self.ratios.loc[common_idx]
        self.metrics = self.metrics.loc[common_idx]
        self.is_ = self.is_.loc[common_idx]
        failed_msg = "Dataframe filtering failed"
        assert self.ratios.index.equals(self.metrics.index), failed_msg
        assert self.ratios.index.equals(self.is_.index), failed_msg

    
    