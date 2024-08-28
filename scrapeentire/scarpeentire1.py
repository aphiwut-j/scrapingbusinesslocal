import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv

def extract_page_content(url, page_type=None):
    try:
        # Append page_type to the URL if provided (e.g., "about", "contact")
        if page_type:
            url = url.rstrip('/') + '/' + page_type
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the entire page content
        page_content = soup.get_text(separator='\n', strip=True)

        # Return the extracted content
        return page_content if page_content.strip() else 'N/A'
    
    except requests.exceptions.RequestException as e:
        return 'N/A'  # Return 'N/A' if there's an error

# Attempt to read CSV file with error handling
try:
    df = pd.read_csv('100lines.csv', sep=',', quotechar='"')

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
            # Extract main page content
            main_content = extract_page_content(url)
            
            # Extract "About" page content
            about_content = extract_page_content(url, 'about')
            
            # Extract "Contact" page content
            contact_content = extract_page_content(url, 'contact')

            log_entry = f"Content for {url}:\n"
            log_entry += f"Main Page Error: {'N/A' if main_content != 'N/A' else 'Failed to fetch'}\n"
            log_entry += f"About Page Error: {'N/A' if about_content != 'N/A' else 'Failed to fetch'}\n"
            log_entry += f"Contact Page Error: {'N/A' if contact_content != 'N/A' else 'Failed to fetch'}\n"
            log_entry += '---------------------------------------------------------------\n\n\n'
            logfile.write(log_entry)
            print(log_entry)

            # Append the page content to the list
            extracted_data.append({
                'url': url,
                'page_content': main_content,
                'about': about_content,
                'contact': contact_content,
            })

# Convert the list of dictionaries to a DataFrame and save it as a CSV
extracted_df = pd.DataFrame(extracted_data)
extracted_df.to_csv(output_filename, index=False, quoting=csv.QUOTE_NONNUMERIC)

print(f"Log file created: {log_filename}")
print(f"Extracted content saved to: {output_filename}")
