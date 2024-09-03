import pandas as pd
import re
from bs4 import BeautifulSoup
import spacy
import os

# Load SpaCy model
nlp = spacy.load('en_core_web_sm')

def extract_data(html_content):
    """
    Extracts email, phone number, name, and a business description from HTML content.
    
    Args:
        html_content (str): HTML content to extract data from.
    
    Returns:
        tuple: Extracted email, phone number, name, and description.
    """
    if not html_content:
        return "No email found", "No phone number found", "No name found", "No description found"

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Email extraction
    email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    email_match = email_pattern.findall(soup.get_text())
    email = email_match[0] if email_match else "No email found"
    
    # Phone extraction with improved regex
    phone_pattern = re.compile(r'\+?\d[\d\s-]{7,}\d')
    phone_match = phone_pattern.findall(soup.get_text())
    phone = phone_match[0] if phone_match else "No phone number found"

    # Extracting name from title, h1, h2, h3, or other headings
    name = None
    if soup.title and soup.title.string:
        name = soup.title.string.strip()
    else:
        meta_name = soup.find('meta', property='og:site_name')
        if meta_name and meta_name.get('content'):
            name = meta_name['content'].strip()
        else:
            for tag in ['h1', 'h2', 'h3']:
                element = soup.find(tag)
                if element:
                    name = element.get_text(strip=True)
                    break

    if not name:
        name = "No name found"

    # Description extraction
    description = None

    # Try meta descriptions first
    meta_description = soup.find('meta', attrs={'name': 'description'})
    if meta_description:
        description = meta_description.get('content')

    if not description:
        og_description = soup.find('meta', property='og:description')
        if og_description:
            description = og_description.get('content')

    if not description:
        twitter_description = soup.find('meta', attrs={'name': 'twitter:description'})
        if twitter_description:
            description = twitter_description.get('content')

    # Fallback to finding descriptive paragraphs
    if not description:
        paragraphs = soup.find_all('p')
        filtered_paragraphs = []
        for paragraph in paragraphs:
            text = paragraph.get_text(strip=True)
            if len(text) > 100 and not any(keyword in text.lower() for keyword in ["home", "menu", "login", "contact", "join", "about", "privacy"]):
                filtered_paragraphs.append(text)
        
        if filtered_paragraphs:
            description = ' '.join(filtered_paragraphs[:2])
            description = ' '.join(description.split()[:100])

    # Use NLP to refine the description
    if not description:
        doc = nlp(soup.get_text())
        for sentence in doc.sents:
            if len(sentence.text) > 100 and not any(keyword in sentence.text.lower() for keyword in ["home", "menu", "login", "contact", "join", "about", "privacy"]):
                description = sentence.text
                break

    if not description:
        description = "No description found"

    return email, phone, name, description

def process_data_from_csv(csv_path):
    """
    Processes data from a CSV file and extracts email, phone number, name, and description.
    
    Args:
        csv_path (str): Path to the CSV file.
    
    Returns:
        list: List of dictionaries containing the extracted data.
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print("File not found. Please check the file path.")
        return []
    except pd.errors.EmptyDataError:
        print("File is empty. Please check the file contents.")
        return []
    except pd.errors.ParserError:
        print("Error parsing the file. Please check the file format.")
        return []

    results = []
    for index, row in df.iterrows():
        page_content = row['page_content']
        if pd.isnull(page_content):
            results.append({
                "URL": row['url'],
                "Email": "No email found",
                "Phone": "No phone number found",
                "Name": "No name found",
                "Description": "No description found"
            })
        else:
            email, phone, name, description = extract_data(page_content)
            results.append({
                "URL": row['url'],
                "Email": email,
                "Phone": phone,
                "Name": name,
                "Description": description
            })
    return results

# Setting up the file path
csv_directory = r'C:\Internship\Web scrap\1.0'
csv_filename = 'scraped_content_20240827_160123.csv'
csv_path = os.path.join(csv_directory, csv_filename)

results = process_data_from_csv(csv_path)
for result in results:
    print(
        f"Website: {result['URL']}\n"
        f"Email: {result['Email']}\n"
        f"Phone: {result['Phone']}\n"
        f"Name: {result['Name']}\n"
        f"Description: {result['Description']}\n"
        "-----------------------------\n"
    )
