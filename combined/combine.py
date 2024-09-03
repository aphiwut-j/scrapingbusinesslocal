import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import base64
from datetime import datetime
import csv
import time
import os
import google.generativeai as genai
from google.generativeai.types.generation_types import StopCandidateException
from google.api_core.exceptions import ResourceExhausted
import sys

# Increase the CSV field size limit
csv.field_size_limit(sys.maxsize)

# Set up the Gemini API
genai.configure(api_key=os.environ["API_KEY"])

# Define the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

class WebScraper:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.df = self._load_csv()
        self.log_filename = datetime.now().strftime("output/scrape_log_%Y%m%d_%H%M%S.log")
        self.output_filename = datetime.now().strftime("output/scraped_content_%Y%m%d_%H%M%S.csv")
        self.extracted_data = []

    def _load_csv(self):
        try:
            df = pd.read_csv(self.csv_file, sep=',', quotechar='"')
            if 'website' not in df.columns:
                raise ValueError("Expected 'website' column not found in the CSV file.")
            df.columns = df.columns.str.strip().str.replace('"', '')
            return df
        except pd.errors.ParserError as e:
            print(f"Error reading CSV file: {e}")
            exit(1)
        except ValueError as e:
            print(f"ValueError: {e}")
            exit(1)

    def extract_page_content(self, url, page_type=None):
        try:
            if page_type:
                # Fetch the main page content first
                response = requests.get(url, timeout=120)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                # Find URLs that start with the specified page_type
                links = soup.find_all('a', href=True)
                matching_url = None
                for link in links:
                    href = link['href']
                    full_url = href if 'http' in href else requests.compat.urljoin(url, href)
                    if full_url.startswith(requests.compat.urljoin(url, page_type)):
                        matching_url = full_url
                        break
                if not matching_url:
                    return 'N/A', 'N/A', f"No matching page found for '{page_type}'"
                url = matching_url

            response = requests.get(url, timeout=120)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            page_content = soup.get_text(separator='\n', strip=True)
            
            # Extract the first image and encode it as base64
            img_tags = soup.find_all('img')
            logo_base64 = 'N/A'
            if img_tags:
                img_url = img_tags[0].get('src')
                if img_url:
                    # Handle both relative and absolute URLs
                    if not img_url.startswith(('http:', 'https:')):
                        img_url = requests.compat.urljoin(url, img_url)
                    try:
                        img_response = requests.get(img_url)
                        img_response.raise_for_status()
                        img_data = BytesIO(img_response.content)
                        try:
                            image = Image.open(img_data)
                            buffered = BytesIO()
                            image.save(buffered, format="PNG")
                            logo_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                        except (OSError, UnidentifiedImageError) as e:
                            print(f"Error processing image from {img_url}: {e}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error fetching image from {img_url}: {e}")
            
            return page_content if page_content.strip() else 'N/A', logo_base64, None
        except requests.exceptions.RequestException as e:
            return 'N/A', 'N/A', str(e)

    def scrape(self):
        with open(self.log_filename, 'w') as logfile:
            for index, row in self.df.iterrows():
                url = row['website']
                if pd.notna(url):
                    # Extract content from main page
                    main_content, logo_base64, main_error = self.extract_page_content(url)
                    # Extract content from about page
                    about_content, _, about_error = self.extract_page_content(url, 'about')
                    # Extract content from contact page
                    contact_content, _, contact_error = self.extract_page_content(url, 'contact')

                    log_entry = (
                        f"Content for {url}:\n"
                        f"Main Page Error: {'N/A' if main_error is None else main_error}\n"
                        f"About Page Error: {'N/A' if about_error is None else about_error}\n"
                        f"Contact Page Error: {'N/A' if contact_error is None else contact_error}\n"
                        '---------------------------------------------------------------\n\n\n'
                    )
                    logfile.write(log_entry)
                    print(log_entry)

                    error_code = ', '.join(filter(None, [main_error, about_error, contact_error])) or 'None'

                    self.extracted_data.append({
                        'url': url,
                        'page_content': main_content,
                        'about_content': about_content,
                        'contact_content': contact_content,
                        'logo': logo_base64,
                        'error': error_code,
                    })

        extracted_df = pd.DataFrame(self.extracted_data)
        extracted_df.to_csv(self.output_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(f"Log file created: {self.log_filename}")
        print(f"Extracted content saved to: {self.output_filename}")

        # Pass the output filename to the summarization process
        return self.output_filename

class ContentSummarizer:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        # Generate a unique filename with date and time
        self.output_csv_file = datetime.now().strftime("output/summarized_content_%Y%m%d_%H%M%S.csv")

    def summarize_and_save_response(self):
        results = []

        # Read the CSV file
        with open(self.csv_file, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                url = row['url']
                page_content = row['page_content']
                about_content = row['about_content']
                contact_content = row['contact_content']
                error = row['error']

                # Summarize page content
                page_summary = self.get_summary(page_content)
                # Summarize about content
                about_summary = self.get_summary(about_content)
                # Summarize contact content
                contact_summary = self.get_summary(contact_content)

                # Append the result to the list
                results.append({
                    "url": url,
                    "extracted_content": page_summary,
                    "extracted_about": about_summary,
                    "extracted_contact": contact_summary
                })

        # Read the existing data
        df = pd.read_csv(self.csv_file)

        # Merge the new responses with the existing data
        df = df.merge(pd.DataFrame(results), on='url', how='left')

        # Write results to a new CSV file
        df.to_csv(self.output_csv_file, index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(f"Responses saved to {self.output_csv_file}")

    def get_summary(self, content):
        if content.lower().strip() == 'n/a' or not content:
            return "n/a"
        else:
            chat_session = model.start_chat(history=[])

            prompt = f"""
            Please extract and summarize the following content. 

            Extract the address, contact number, and name, and return the information in the following JSON format:

            {{
                "address": "<address>",
                "contact_number": "<contact_number>",
                "name": "<name>",
                "about": "<about>"
            }}

            If any of this information is not available or unclear, use "n/a" for that field.

            Content:

            "{content}"
            """
            retry_count = 0
            while retry_count < 5:  # Maximum of 5 retries
                try:
                    response = chat_session.send_message(prompt)
                    print(f"Gemini Response: {response.text.strip()}")  # Print response for debugging
                    return response.text.strip()
                except StopCandidateException as e:
                    print(f"Safety issue encountered: {e}")
                    return "Safety issue, response not generated"
                except ResourceExhausted as e:
                    retry_count += 1
                    wait_time = 2 ** retry_count  # Exponential backoff
                    print(f"Quota exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    return "Unexpected error, response not generated"

if __name__ == "__main__":
    # Step 1: Scrape the websites
    scraper = WebScraper(csv_file='data/5lines.csv')
    scraped_csv_file = scraper.scrape()

    # Step 2: Summarize the content using Gemini API
    summarizer = ContentSummarizer(csv_file=scraped_csv_file)
    summarizer.summarize_and_save_response()
