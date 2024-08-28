import pandas as pd
import base64
from io import BytesIO
from PIL import Image

# Read the CSV file
csv_file = 'websites_with_logos.csv'
df = pd.read_csv(csv_file)

# Function to decode base64 and display the image
def display_image_from_base64(base64_string):
    try:
        # Decode the base64 string to bytes
        image_data = base64.b64decode(base64_string)
        
        # Convert bytes to a PIL Image
        image = Image.open(BytesIO(image_data))
        
        # Display the image
        image.show()

    except Exception as e:
        print(f'Error displaying image: {e}')

# Example: Display the logo for a specific row (e.g., the first row)
if 'logo_base64' in df.columns:
    for index, row in df.iterrows():
        base64_string = row['logo_base64']
        if pd.notna(base64_string):  # Check if the base64 string is not NaN
            print(f"Displaying image for website: {row['website']}")
            display_image_from_base64(base64_string)
else:
    print("No 'logo_base64' column found in the CSV file.")
