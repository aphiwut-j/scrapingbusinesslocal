import pandas as pd
import requests
from bs4 import BeautifulSoup
import base64
from io import BytesIO

# Read CSV file
csv_file = '5lines.csv'
df = pd.read_csv(csv_file)

# Function to download logo and convert it to base64
def download_and_encode_logo(website_url):
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
            img_response = requests.get(img_url)
            img_response.raise_for_status()  # Check for request errors

            # Encode image in base64
            img_base64 = base64.b64encode(img_response.content).decode('utf-8')
            return img_base64
        else:
            print(f'No logo found for {website_url}')
            return None

    except Exception as e:
        print(f'Error downloading logo from {website_url}: {e}')
        return None

# Create a new DataFrame to store the results
results = []

# Iterate through each row in the DataFrame
for index, row in df.iterrows():
    website = row['website']
    email = row['email']
    user_id = row['user_id']
    
    # Download and encode the logo
    logo_base64 = download_and_encode_logo(website)
    
    # Store the result
    results.append({
        'email': email,
        'user_id': user_id,
        'website': website,
        'logo_base64': logo_base64
    })

# Create a DataFrame with the results
df_results = pd.DataFrame(results)

# Save the DataFrame to a new CSV file
df_results.to_csv('websites_with_logos.csv', index=False)
