import pandas as pd
import json
import re

# Load the CSV file into a pandas DataFrame
try:
    df = pd.read_csv('output/summarized_content_20240903_163746.csv')  # Replace with your actual file path
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit(1)

# Function to clean JSON content
def clean_json_content(content):
    # Remove any non-JSON content such as extra backticks or unexpected characters
    content = re.sub(r'^```json', '', content)  # Remove leading ```json if present
    content = re.sub(r'```$', '', content)       # Remove trailing ```
    content = content.strip()
    # Ensure that the content starts and ends with valid JSON brackets
    if not (content.startswith('{') and content.endswith('}')):
        return None
    return content

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    content = row['extracted_content']
    
    # Print the raw content for debugging
    print(f"Raw content for row {index}: {content}")
    
    # Check if the content is NaN or not a string
    if pd.isna(content) or not isinstance(content, str):
        print(f"Row {index} has no valid JSON content or is empty.")
        continue
    
    # Clean and check if content is valid
    cleaned_content = clean_json_content(content)
    
    if cleaned_content:
        try:
            # Parse the JSON content
            json_content = json.loads(cleaned_content)
            # Print each value from the JSON
            print(f"Row {index} - Name: {json_content.get('name', 'N/A')}")
            print(f"Row {index} - Address: {json_content.get('address', 'N/A')}")
            print(f"Row {index} - Contact Number: {json_content.get('contact_number', 'N/A')}")
            print(f"Row {index} - About: {json_content.get('about', 'N/A')}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for row {index}: {e}")
    else:
        print(f"Row {index} has invalid JSON content.")
    
    print("-" * 40)  # Separator for readability
