from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import time
from openai import OpenAI
import pandas as pd
from langdetect import detect
from tqdm import tqdm

def is_not_english(text):
    try:
        return detect(text) != 'en'
    except:
        return False

def get_translation(client, name):
    prompt = f"""Translate the product name "{name}" to English and return it under the json key "translatedText"."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

client = OpenAI(api_key=os.environ.get('openai_key', "key"))
def translate_to_english(row):
    unprocessed_text = row['Name']
    
    max_retries = 100
    retry_count = 0
    sleep_interval = 1  # seconds

    while retry_count < max_retries:
        try:
            translated_text = get_translation(client, unprocessed_text)
            translated_text = json.loads(translated_text)
            return translated_text["translatedText"]
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                return "unable to translate"
            time.sleep(sleep_interval)

def translate(translator=translate_to_english, filter=False):
    # Read the DataFrame from a CSV file
    df = pd.read_csv('product_details_price.csv')
    # df = df.sample(100)

    # Initialize 'Name_translated' with 'Name'
    df['Name_translated'] = df['Name']
    
    # Filter out non-English rows if needed
    if filter:
        tqdm.pandas(desc="Filtering")
        non_english_rows = df[df['Name'].progress_apply(is_not_english)]
        rows_to_translate = non_english_rows
    else:
        rows_to_translate = df

    # Using ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=25) as executor:
        # Create a future for each row to be translated
        futures = {executor.submit(translator, row): index for index, row in rows_to_translate.iterrows()}

        checkpoint_counter = 0

        # Wrap tqdm around as_completed to track progress
        for future in tqdm(as_completed(list(futures.keys())), total=len(futures), desc="Translating Text"):
            result = future.result()
            index = futures[future]
            df.at[index, 'Name_translated'] = result

            checkpoint_counter += 1
            # Write to the CSV file at each checkpoint interval
            if checkpoint_counter % 100 == 0:
                df.to_csv('product_details_final.csv', index=False)

    # Write the modified DataFrame to a new CSV file
    df.to_csv('product_details_final.csv', index=False)

def main():
    translate(translator=translate_to_english)

if __name__ == '__main__':
    main()