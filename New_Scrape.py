import requests
from bs4 import BeautifulSoup
import csv

# Function to fetch page content
def fetch_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

# Function to find the URLs of specific pages
def find_page_urls(main_url):
    page_urls = {'Home': main_url}
    response = requests.get(main_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href'].lower()
            if 'about' in href:
                page_urls['About'] = href if 'http' in href else main_url + href
            elif 'contact' in href:
                page_urls['Contact'] = href if 'http' in href else main_url + href
        
    return page_urls

# Function to convert HTML to plain text
def html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

# Main domain URL (replace with actual domain)
main_url = 'https://www.vitachiropractic.com.au'

# Fetch URLs for Home, About, and Contact pages
page_urls = find_page_urls(main_url)

# Dictionary to store the content
page_contents = {}

# Fetch the content for each page and convert to text
for page_name, url in page_urls.items():
    content = fetch_page_content(url)
    if content:
        text_content = html_to_text(content)
        page_contents[page_name] = text_content
    else:
        print(f"Failed to fetch content from {url}")

# Write the content to a CSV file
with open('website_content.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Page', 'Content'])  # CSV header
    for page_name, content in page_contents.items():
        writer.writerow([page_name, content])

print("Content saved to website_content.csv")

