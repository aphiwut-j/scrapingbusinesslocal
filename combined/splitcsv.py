import pandas as pd

def split_csv(input_file, output_file_1, output_file_2):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Calculate the halfway point
    half_idx = len(df) // 2
    
    # Split the data into two halves
    df1 = df.iloc[:half_idx]
    df2 = df.iloc[half_idx:]
    
    # Write each half to separate CSV files
    df1.to_csv(output_file_1, index=False)
    df2.to_csv(output_file_2, index=False)
    
    print(f"CSV split completed: {output_file_1} and {output_file_2}")

# Usage example
input_file = '/Users/aphiwutjanphet/Documents/internship/Business Local/github/scrapingbusinesslocal/combined/output/cleant json/output3-.csv'
output_file_1 = '/Users/aphiwutjanphet/Documents/internship/Business Local/github/scrapingbusinesslocal/combined/output/cleant json/output5.csv'
output_file_2 = '/Users/aphiwutjanphet/Documents/internship/Business Local/github/scrapingbusinesslocal/combined/output/cleant json/output6.csv'

split_csv(input_file, output_file_1, output_file_2)
