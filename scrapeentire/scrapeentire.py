import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv  # Import csv module for quoting options

def extract_page_content(url):
    try:
        response = requests.get(url, timeout=30)  # Add timeout to handle hanging requests
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the entire page content
        page_content = soup.get_text(separator='\n', strip=True)  # Get visible text content

        # Return a dictionary with the URL and page content
        return {
            'url': url,
            'page_content': page_content if page_content.strip() else 'N/A',
            'error': None
        }
    except requests.exceptions.RequestException as e:
        # Log the request error and return 'N/A' for page content
        return {
            'url': url,
            'page_content': 'N/A',
            'error': str(e)
        }

# Attempt to read CSV file with error handling
try:
    # Read the CSV file with proper handling
    df = pd.read_csv('100lines.csv', sep=',', quotechar='"')

    # Check for the 'website' column
    if 'website' not in df.columns:
        raise ValueError("Expected 'website' column not found in the CSV file.")
    
    # Clean the column names
    df.columns = df.columns.str.strip().str.replace('"', '')

except pd.errors.ParserError as e:
    print(f"Error reading CSV file: {e}")
    exit(1)
except ValueError as e:
    print(f"ValueError: {e}")
    exit(1)

# Create a log file with a timestamp
log_filename = datetime.now().strftime("scrape_log_%Y%m%d_%H%M%S.log")
output_filename = datetime.now().strftime("scraped_content_%Y%m%d_%H%M%S.csv")

# List to hold all extracted data for saving to a new CSV
extracted_data = []

with open(log_filename, 'w') as logfile:
    for index, row in df.iterrows():
        url = row['website']
        if pd.notna(url):
            page_details = extract_page_content(url)
            log_entry = f"Content for {url}:\n"
            log_entry += f"Error (if any): {page_details['error']}\n"
            log_entry += '--------------------------------------------------------------- \n \n \n'
            logfile.write(log_entry)
            print(log_entry)

            # Append the page content to the list
            extracted_data.append({
                'url': url,
                'page_content': page_details['page_content'],
                'error': page_details['error']
            })

# Convert the list of dictionaries to a DataFrame and save it as a CSV
extracted_df = pd.DataFrame(extracted_data)
extracted_df.to_csv(output_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)

print(f"Log file created: {log_filename}")
print(f"Extracted content saved to: {output_filename}")
