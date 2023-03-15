import pandas as pd
from typing import Dict, List, Tuple



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

    def __init__(self, data_dictionary: Dict):
        self.data_dictionary = data_dictionary
        # self.info = self.parse_info()
        # self.ratios = self.parse_ratios()
        # self.metrics = self.parse_metrics()
        # self.is_ = self.parse_income_statement()
        # self.price = self.parse_price()

    @staticmethod
    def json_to_dataframe(json_data):
        return pd.DataFrame(json_data)
    


    
    