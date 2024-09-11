import pandas as pd
from datetime import datetime

df = pd.read_csv('/Users/aphiwutjanphet/Documents/internship/Business Local/github/scrapingbusinesslocal/combined/output/cleant json/cleaned_content_20240911_101327.csv')

# Define columns to check
columns_to_check = ['page_content', 'about_content', 'contact_content']

# Define extracted columns that contain the information you want to compare
extracted_columns_mapping = {
    'extracted_content_Name': 'name_found',
    'extracted_content_Address': 'address_found',
    'extracted_content_Contact_Number': 'number_found',
    'extracted_content_Email': 'email_found',
    'extracted_contact_Name': 'name_found',
    'extracted_contact_Address': 'address_found',
    'extracted_contact_Contact_Number': 'number_found',
    'extracted_contact_Email': 'email_found'
}

# Function to check if extracted content is in any of the first 3 columns
def check_information(row):
    # Loop through each extracted column
    for extracted_col, result_col in extracted_columns_mapping.items():
        extracted_value = row[extracted_col]
        
        # Check if the extracted value exists and is not NaN
        if pd.notna(extracted_value):
            # Assume not found initially
            found = False
            match = False
            
            # Check if the extracted value is present in any of the 'page_content', 'about_content', 'contact_content' columns
            for col in columns_to_check:
                if extracted_value in str(row[col]):  # Check if extracted_value is a substring in the column
                    found = True
                    break  # Stop checking other columns once found
            
            # Override based on the result but only for the specific result_col
            if found:
                row[result_col] = 1  # Found and matched
            else:
                row[result_col] = 0  # Not found
    
    return row

# Apply the function row-wise to check and update the columns
df = df.apply(check_information, axis=1)

# Save the updated DataFrame to a new CSV file
df.to_csv(datetime.now().strftime('/Users/aphiwutjanphet/Documents/internship/Business Local/github/scrapingbusinesslocal/combined/output/evaluation results/result_%Y%m%d_%H%M%S.csv'), index=False) # index=False to avoid saving the row indices

# Now you can view the updated DataFrame with overridden columns
print(df[['page_content', 'about_content', 'contact_content', 'name_found', 'address_found', 'number_found', 'email_found']])
