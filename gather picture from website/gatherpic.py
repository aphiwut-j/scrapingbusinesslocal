import requests
from bs4 import BeautifulSoup
import os

# Specify the URL of the website
url = 'https://www.bayviewgolfclub.com.au'

# Send a request to the website and get the HTML content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all image tags
img_tags = soup.find_all('img')

# Create a directory to save the images
os.makedirs('logos', exist_ok=True)

# Loop through the image tags
for img in img_tags:
    img_url = img.get('src')
    if img_url and 'logo' in img_url.lower():  # Filter for logos
        # Make sure the URL is absolute
        img_url = requests.compat.urljoin(url, img_url)
        
        # Get the base name of the image file
        img_name = os.path.basename(img_url)
        
        # Append '_logo' before the file extension
        name, ext = os.path.splitext(img_name)
        img_name = f'{name}_logo{ext}'
        
        # Save the image
        img_data = requests.get(img_url).content
        img_path = os.path.join('logos', img_name)
        with open(img_path, 'wb') as handler:
            handler.write(img_data)
        
        print(f'Logo saved: {img_name}')
