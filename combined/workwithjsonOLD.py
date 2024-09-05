import pandas as pd
import json
import re
import csv
from datetime import datetime

# Load the CSV file into a pandas DataFrame
path = 'output/cleant dataset/summarized_content_20240904_153512.csv'
try:
    df = pd.read_csv(path)  # Replace with your actual file path
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

# Prepare a list to store the rows for the new CSV
output_rows = []

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Copy the original row data
    new_row = row.copy()

    # Get the content from the three columns
    content_list = ['extracted_content', 'extracted_about', 'extracted_contact']
    
    extracted_data = {}
    
    for col in content_list:
        content = row.get(col, None)
        
        # Check if the content is NaN or not a string
        if pd.isna(content) or not isinstance(content, str):
            print(f"Row {index} in column {col} has no valid JSON content or is empty.")
            continue
        
        # Clean and check if content is valid
        cleaned_content = clean_json_content(content)
        
        if cleaned_content:
            try:
                # Parse the JSON content
                json_content = json.loads(cleaned_content)
                # Extract required fields
                name = json_content.get('name', 'N/A')
                address = json_content.get('address', 'N/A')
                contact_number = json_content.get('contact_number', 'N/A')
                about = json_content.get('about', 'N/A')
                
                # Store the extracted information per column in the dictionary
                extracted_data[f'{col}_Name'] = name
                extracted_data[f'{col}_Address'] = address
                extracted_data[f'{col}_Contact_Number'] = contact_number
                extracted_data[f'{col}_About'] = about
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for row {index} in column {col}: {e}")
        else:
            print(f"Row {index} in column {col} has invalid JSON content.")
    
    # Add extracted data to the new row
    for key, value in extracted_data.items():
        new_row[key] = value

    # Append the modified row (with both the original data and extracted data) to output_rows
    output_rows.append(new_row)

    print("-" * 40)  # Separator for readability

# Create a DataFrame from the output rows
output_df = pd.DataFrame(output_rows)

# Save the DataFrame with both original and extracted columns to a new CSV file
output_filename = datetime.now().strftime('output/cleant json/cleaned_content_%Y%m%d_%H%M%S.csv')
output_df.to_csv(output_filename, index=False)

print(f"Saved the cleaned content with original columns to {output_filename}")