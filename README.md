# Klarna Product Page Dataset Utilities

This repository contains a set of utilities designed to process and analyze the Klarna Product Page Dataset https://github.com/klarna/product-page-dataset 
These utilities are essential for converting the dataset into tabular format, extracting specific data points, 
and translating content to facilitate further analysis and research.

## Utilities Overview

### 1. parse_data_to_csv.py

This script converts the Klarna Product Page Dataset into a CSV format. 
Input folder structure expected is: `data\<locale>\<Website>\<ID>\<Contains .html or .mhtml>`

The resulting CSV file contains the following columns: 
- 'Name': The name of the product.
- 'Main picture': List of URLs to the main image of the product.
- 'Price': The price of the product.
- 'Locale': The market or locale of the product page.
- 'Website': The website or merchant from where the product page is sourced.
- 'ID': A unique identifier for each product page.

This utility is essential for simplifying the dataset into a more accessible and tabular format, 
making it easier for further analysis or machine learning tasks.


### 2. parse_price.py

This script is designed to extract and parse the price information from the 'Price' field of the dataset. 
It utilizes OpenAI's GPT model for parsing, ensuring high accuracy and efficiency in extracting price data. 
This utility is particularly useful for handling various formats and representations of price data 
across different locales and websites in the dataset.


### 3. translate_to_english.py

This utility focuses on translating the 'Name' field of the dataset from various languages to English. 
It is crucial for standardizing the dataset, especially when dealing with product pages from different locales. 
This translation facilitates easier analysis and accessibility of the dataset for English-speaking researchers or analysts.


## Usage

Each script can be run independently based on the specific requirements of the dataset processing. 
Ensure that the necessary Python packages are installed and that the dataset is accessible in the expected format.

## Contribution

Contributions to improve these utilities or to add new functionalities are welcome. 
Please follow the standard pull request process for contributions.

## Author
Ashutosh Engavle
https://www.linkedin.com/in/ashutosh-engavle/
