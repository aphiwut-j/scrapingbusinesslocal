import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image, UnidentifiedImageError  # Correct import
import base64
from datetime import datetime
import csv

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
                url = url.rstrip('/') + '/' + page_type
            response = requests.get(url, timeout=30)
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
                        img_response.raise_for_status()  # Ensure the request was successful
                        img_data = BytesIO(img_response.content)
                        try:
                            image = Image.open(img_data)
                            buffered = BytesIO()
                            image.save(buffered, format="PNG")
                            logo_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                        except (OSError, UnidentifiedImageError) as e:  # Correct exception
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
                        'about': about_content,
                        'contact': contact_content,
                        'logo': logo_base64,
                        'error': error_code,
                    })

        extracted_df = pd.DataFrame(self.extracted_data)
        extracted_df.to_csv(self.output_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(f"Log file created: {self.log_filename}")
        print(f"Extracted content saved to: {self.output_filename}")


class ImageDisplayer:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.df = self._load_csv()

    def _load_csv(self):
        try:
            return pd.read_csv(self.csv_file)
        except pd.errors.ParserError as e:
            print(f"Error reading CSV file: {e}")
            exit(1)
        except ValueError as e:
            print(f"ValueError: {e}")
            exit(1)

    def display_image_from_base64(self, base64_string):
        try:
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data))
            image.show()
        except Exception as e:
            print(f'Error displaying image: {e}')

    def display_images(self):
        if 'logo' in self.df.columns:
            for index, row in self.df.iterrows():
                base64_string = row['logo']
                if pd.notna(base64_string) and base64_string != 'N/A':
                    print(f"Displaying image for website: {row['url']}")
                    self.display_image_from_base64(base64_string)
        else:
            print("No 'logo' column found in the CSV file.")


if __name__ == "__main__":
    # Usage example for scraping
    scraper = WebScraper(csv_file='data/100lines.csv')
    scraper.scrape()

    # Usage example for displaying images
    # image_displayer = ImageDisplayer(csv_file='scraped_content_YYYYMMDD_HHMMSS.csv')
    # image_displayer.display_images()
