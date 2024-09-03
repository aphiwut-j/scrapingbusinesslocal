import requests
from bs4 import BeautifulSoup
import pandas as pd

def find_links(url, keywords):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # Find all links in the page
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Check if the link contains any of the keywords
            if any(keyword in href.lower() for keyword in keywords):
                links.append(href)
                
        return links
    
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def crawl_website(start_url, keywords):
    visited = set()
    to_visit = [start_url]
    found_links = []

    while to_visit:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        
        print(f"Crawling: {url}")
        links = find_links(url, keywords)
        found_links.extend(links)
        
        # Add new links to the queue
        for link in links:
            if link.startswith('http') and link not in visited:
                to_visit.append(link)
    
    return found_links

# Main URL to start crawling
start_url = 'https://e1poolcertifier.com'
# Keywords to look for in URLs
keywords = ['about', 'contact']

# Crawl the website
found_links = crawl_website(start_url, keywords)

# Save the results to a CSV file
df = pd.DataFrame(found_links, columns=['URL'])
df.to_csv('found_links.csv', index=False)

print("Found links have been saved to found_links.csv")
