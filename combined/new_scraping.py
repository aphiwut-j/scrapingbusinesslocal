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
    "temperature": 0.0,
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
    def __init__(self, csv_file, keywords):
        self.csv_file = csv_file
        self.keywords = keywords
        self.log_filename = datetime.now().strftime("output/scrape_log_%Y%m%d_%H%M%S.log")
        self.output_filename = datetime.now().strftime("output/scraped_content_%Y%m%d_%H%M%S.csv")
        self.extracted_data = []

    def load_urls(self):
        try:
            df = pd.read_csv(self.csv_file)
            urls = df['website'].dropna().tolist()
            return urls
        except Exception as e:
            print(f"Error loading URLs from CSV: {e}")
            return []

    def find_links(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            links = [link['href'] for link in soup.find_all('a', href=True) if any(keyword in link['href'].lower() for keyword in self.keywords)]
            return links
        except Exception as e:
            print(f"Error fetching links from {url}: {e}")
            return []

    def extract_page_content(self, url, page_type=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = self.fetch_with_retry(url, headers=headers)
            if not response:
                return 'N/A', 'N/A', "Failed to fetch the page"
                
            soup = BeautifulSoup(response.content, 'html.parser')
            page_content = soup.get_text(separator='\n', strip=True)

            logo_base64 = 'N/A'
            img_tags = soup.find_all('img')
            if img_tags:
                img_url = img_tags[0].get('src')
                if img_url:
                    if not img_url.startswith(('http:', 'https:')):
                        img_url = requests.compat.urljoin(url, img_url)
                    try:
                        img_response = requests.get(img_url, headers=headers)
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

    def fetch_with_retry(self, url, headers=None, retries=3):
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}: Error fetching {url}: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def scrape(self):
        urls = self.load_urls()
        with open(self.log_filename, 'w') as logfile:
            for url in urls:
                if url:
                    main_content, logo_base64, main_error = self.extract_page_content(url)
                    about_content, _, about_error = self.extract_page_content(url, 'about')
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

        return self.output_filename

class ContentSummarizer:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.output_csv_file = datetime.now().strftime("output/summarized_content_%Y%m%d_%H%M%S.csv")

    def summarize_and_save_response(self):
        results = []

        try:
            with open(self.csv_file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    url = row['url']
                    page_content = row['page_content']
                    about_content = row['about_content']
                    contact_content = row['contact_content']
                    error = row['error']

                    page_summary = self.get_summary(page_content)
                    about_summary = self.get_summary(about_content)
                    contact_summary = self.get_summary(contact_content)

                    results.append({
                        "url": url,
                        "extracted_content": page_summary,
                        "extracted_about": about_summary,
                        "extracted_contact": contact_summary
                    })

            df = pd.read_csv(self.csv_file)
            df = df.merge(pd.DataFrame(results), on='url', how='left')
            df.to_csv(self.output_csv_file, index=False, quoting=csv.QUOTE_NONNUMERIC)

            print(f"Responses saved to {self.output_csv_file}")
        except Exception as e:
            print(f"Error summarizing content: {e}")

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
            while retry_count < 5:
                try:
                    response = chat_session.send_message(prompt)
                    response_text = response.text.strip()
                    print(f"Gemini Response: {response_text}")
                    return response_text
                except StopCandidateException as e:
                    print(f"Safety issue encountered: {e}")
                    return "Safety issue, response not generated"
                except ResourceExhausted as e:
                    retry_count += 1
                    wait_time = 2 ** retry_count
                    print(f"Quota exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    return "Unexpected error, response not generated"
            return "Failed after multiple retries"

if __name__ == "__main__":
    # Example usage
    scraper = WebScraper(csv_file='data/5lines.csv', keywords=['contact', 'about'])
    scraper.scrape()

    summarizer = ContentSummarizer(csv_file=scraper.output_filename)
    summarizer.summarize_and_save_response()