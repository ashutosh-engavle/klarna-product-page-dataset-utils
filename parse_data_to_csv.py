import base64
import os
import json
from bs4 import BeautifulSoup
import csv
import re
from tqdm import tqdm
import email

# MHTML
def decode_content(content, encodings=('utf-8', 'ISO-8859-1', 'windows-1252')):
    for encoding in encodings:
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("Unable to decode content with the provided encodings.")

# MHTML
def mhtml_to_html(mhtml_path):
    html_content = ""
    with open(mhtml_path, "r") as file:
        message = email.message_from_file(file)
        for part in message.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset()
                try:
                    html_content = payload.decode(charset) if charset else payload.decode('utf-8')
                except UnicodeDecodeError:
                    html_content = decode_content(payload)
                break
    return html_content

# HTML
def extract_all_urls_from_element(element):
    url_pattern = re.compile(r'https?://\S+')  # Pattern to identify URLs
    urls = []

    if element:
        # Check if the element itself has a URL in src
        if 'src' in element.attrs and url_pattern.search(element['src']):
            urls.append(element['src'])

        # Then search for URLs in all attributes of nested tags
        for tag in element.find_all(recursive=True):
            for attr, value in tag.attrs.items():
                if isinstance(value, str) and url_pattern.search(value):
                    urls.append(value)

    return urls

# HTML + MHTML
def extract_elements_with_headers(html_soup, labels, locale, website, id, file_type):
    # Prepare data for CSV
    data = {'Locale': locale, 'Website': website, 'ID': id}
    for label in labels:
        if label in ["Cart", "Add to Cart"]:  # Skip these labels
            continue

        element = html_soup.find(attrs={"klarna-ai-label": label})
        
        if label == "Main picture":
            content = extract_all_urls_from_element(element)
            data[label] = content
        else:
            data[label] = element.get_text().strip() if element else "Not Found"

    return data

def process_directories(root_dir, csv_file_path):
    # Initialize fieldnames
    fieldnames = ['Locale', 'Website', 'ID']
    labels = ['Name', 'Main picture', 'Price']

    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames + labels)
        writer.writeheader()
        for locale in tqdm(os.listdir(root_dir), desc="Processing Locale", position=0):
            locale_path = os.path.join(root_dir, locale)
            if os.path.isdir(locale_path):
                for website in tqdm(os.listdir(locale_path), desc="Processing Website", position=1, leave=False):
                    website_path = os.path.join(locale_path, website)
                    if os.path.isdir(website_path):
                        for id in tqdm(os.listdir(website_path), desc="Processing ID", position=2, leave=False):
                            id_path = os.path.join(website_path, id)
                            if os.path.isdir(id_path):# and 'page_metadata.json' in os.listdir(id_path):
                                html_exists = 'source.html' in os.listdir(id_path)
                                mhtml_exists = 'source.mhtml' in os.listdir(id_path)

                                if(not html_exists and not mhtml_exists):
                                    continue

                                file_path = os.path.join(id_path, 'source.html' if html_exists else 'source.mhtml')
                                file_type = 'html' if html_exists else 'mhtml'

                                if file_type == 'mhtml':
                                    html_content = mhtml_to_html(file_path)
                                    soup = BeautifulSoup(html_content, 'html.parser')
                                else:
                                    with open(file_path, 'r', encoding='utf-8') as html_file:
                                        soup = BeautifulSoup(html_file, 'html.parser')

                                # Extract data
                                extracted_data = extract_elements_with_headers(soup, labels, locale, website, id, file_type)                                                                    
                                writer.writerow(extracted_data)
                                csvfile.flush()

def main():
    output_csv_path = 'product_details_all.csv'
    for root_dir in ['data']:
        process_directories(root_dir, output_csv_path)

if __name__ == '__main__':
    main()