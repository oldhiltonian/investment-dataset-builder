import pandas as pd
from typing import Dict, List, Tuple
import json
from pathlib import Path 

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
    When parsed, only relevant data is passed back from each of the sub-dictionaries. This
    means that duplicate features are not retured from self.parse_metrics() is that feature
    is already returned from self.parse_ratios().

    """

    def __init__(self, data_dictionary: Dict[str, List]):
        self.data_dictionary = data_dictionary
        self.info = self.parse_info()
        self.ratios = self.parse_ratios()
        self.metrics = self.parse_metrics()
        self.is_ = self.parse_income_statement()
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

    def parse_info(self) -> pd.DataFrame:
        json_data = self.data_dictionary['info']
        cols = ['symbol', 'companyName', 'currency', 'exchange', 'industry', 'sector']
        df_data = self.json_to_dataframe(json_data)
        return df_data[cols]
    
    def parse_ratios(self) -> pd.DataFrame:
        cols = features['ratios']
        json_data = self.data_dictionary['ratios']
        df_data = self.json_to_dataframe(json_data)
        return df_data[cols]
    
    def parse_metrics(self) -> pd.DataFrame:
        cols = features['metrics']
        json_data = self.data_dictionary['metrics']
        df_data = self.json_to_dataframe(json_data)
        return df_data[cols]

    def parse_income_statement(self) -> pd.DataFrame:
        cols = features['is']
        json_data = self.data_dictionary['is']
        df_data = self.json_to_dataframe(json_data)
        return df_data[cols]

    def parse_price(self) -> pd.DataFrame:
        return self.data_dictionary['price'][0]

    
    