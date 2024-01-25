from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import os
import time
from openai import OpenAI
import pandas as pd
from tqdm import tqdm
import json

client = None

def count_rows(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        return sum(1 for _ in csv.reader(csvfile))

def get_price(client, price_string):
    prompt = f"""Convert {price_string} to json with keys price and currency. For ambiguous currency symbols like '$', default to the most common currency (e.g., USD).
        price should only have numeric values and currency cannot have any symbols.
        If price cannot be inferred, default to -1. If currency cannot be inferred, default to "unknown".
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

client = OpenAI(api_key=os.environ.get('openai_key', "key"))
def process_price(row):
    unprocessed_price = row['Price']
    
    max_retries = 10
    retry_count = 0
    sleep_interval = 1  # seconds

    while retry_count < max_retries:
        try:
            processed_price = get_price(client, unprocessed_price)
            processed_price = json.loads(processed_price)
            return pd.Series([float(processed_price['price']), processed_price['currency']], index=['inferred_price', 'inferred_currency'])
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                return pd.Series([-1, 'unknown'], index=['inferred_price', 'inferred_currency'])
            time.sleep(sleep_interval)

def process_csv_with_price(input_csv_file_path, output_csv_file_path):
    # Read the CSV file
    df = pd.read_csv(input_csv_file_path, encoding='utf-8')
    # df = df.sample(100)

    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(process_price, row):index for index, row in df.iterrows()}

        checkpoint_counter = 0

        # Wrap tqdm around as_completed to track progress
        for future in tqdm(as_completed(list(futures.keys())), total=len(futures), desc="Processing Prices"):
            result = future.result()
            index = futures[future]
            df.at[index, 'inferred_price'] = result['inferred_price']
            df.at[index, 'inferred_currency'] = result['inferred_currency']

            checkpoint_counter += 1
            # Write to the CSV file at each checkpoint interval
            if checkpoint_counter % 100 == 0:
                df.to_csv(output_csv_file_path, index=False)

    # Write the processed DataFrame to a new CSV file
    df.to_csv(output_csv_file_path, index=False, encoding='utf-8')

def main():
    input_csv_file_path = 'product_details_all.csv'
    output_csv_file_path = 'product_details_price.csv'
    process_csv_with_price(input_csv_file_path, output_csv_file_path)

if __name__ == '__main__':
    main()