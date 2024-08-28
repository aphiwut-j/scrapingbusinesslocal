import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# Read CSV file
csv_file = '5lines.csv'
df = pd.read_csv(csv_file)

# Create a directory to save logos
if not os.path.exists('logos'):
    os.makedirs('logos')

# Function to download and save logo
def download_logo(website_url, save_path):
    try:
        # Fetch website content
        response = requests.get(website_url)
        response.raise_for_status()  # Check for request errors

        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the logo (usually with <img> tag)
        logo = soup.find('img', {'class': 'logo'}) or soup.find('img', {'id': 'logo'})
        if not logo:
            logo = soup.find('link', {'rel': 'icon'})  # favicon

        if logo:
            img_url = logo['src'] if 'src' in logo.attrs else logo['href']
            if not img_url.startswith('http'):
                img_url = requests.compat.urljoin(website_url, img_url)  # Handle relative URLs

            # Download image
            img_response = requests.get(img_url, stream=True)
            img_response.raise_for_status()  # Check for request errors

            # Save image
            with open(save_path, 'wb') as file:
                file.write(img_response.content)
            print(f'Logo saved to {save_path}')
        else:
            print(f'No logo found for {website_url}')

    except Exception as e:
        print(f'Error downloading logo from {website_url}: {e}')

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    website = row['website']
    email = row['email']
    user_id = row['user_id']
    
    # Define file path
    logo_file_path = os.path.join('logos', f'{user_id}_logo.png')

    # Download and save logo
    download_logo(website, logo_file_path)
