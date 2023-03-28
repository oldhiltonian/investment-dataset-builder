.. _investment-dataset-builder:

Investment Dataset Builder
==========================

Investment Dataset Builder is a Python package designed to build an investment dataset from the financial 
information of publicly traded companies. The package includes three classes: `DataScraper`, `DataParser`, and `DatasetBuilder`. 
The `DataScraper` class scrapes company data from Yahoo Finance and Financial Modelling Prep (FMP) API. 
The `DataParser` class cleans and formats the scraped data. The `DatasetBuilder` class composes the `DataScraper` and `DataParser` classes 
to build an investment dataset from the cleaned and formatted data.

Installation
------------

To install the package, you can clone the repository from GitHub. No installation is required other than insalling the dependencies.


Usage
-----

To use the package, you can create an instance of the `DatasetBuilder` class and specify the stock exchanges from which you want to 
scrape company data. You can then build an investment dataset from the scraped data using the `build_dataset` method.

.. code-block:: python

    from investment_dataset_builder import DatasetBuilder

    # Create a DatasetBuilder object
    builder = DatasetBuilder()

    # Specify the stock exchanges to scrape from
    builder.set_stock_exchanges(['NASDAQ', 'NYSE'])

    # Build the investment dataset
    dataset = builder.build_dataset()

The resulting dataset will include financial ratios and metrics pulled from the Financial Modeling Prep API, as well as historical 
stock data from Yahoo Finance. The data will be aggregated into the same time periods that the companies filed their financial information in.

Optional Classes
----------------

The `DataScraper` and `DataParser` classes can also be used independently of the `DatasetBuilder` class, if desired. The `DataScraper` class 
can be used to scrape company data from Yahoo Finance, and the `DataParser` class can be used to clean and format the scraped data.

.. code-block:: python

    from investment_dataset_builder import DataScraper, DataParser

    # Create a DataScraper object and scrape company data from Yahoo Finance
    scraper = DataScraper()
    data = scraper.scrape_data()

    # Create a DataParser object and clean and format the scraped data
    parser = DataParser()
    cleaned_data = parser.clean_data(data)
    formatted_data = parser.format_data(cleaned_data)


License
-------

This package is licensed under the MIT License. See the `LICENSE` file for more information.