import time
import os
import csv
import google.generativeai as genai
from google.generativeai.types.generation_types import StopCandidateException
from google.api_core.exceptions import ResourceExhausted

# Set up the Gemini API
genai.configure(api_key=os.environ["API_KEY"])

# Define the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Function to process CSV and summarize content
def summarize_and_save_response(csv_file, output_csv_file):
    results = []

    # Read the CSV file
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            url = row['url']
            page_content = row['page_content']
            error = row['error']

            # Skip if content is 'N/A' or an error occurred
            if page_content.lower() == 'n/a' or error:
                response_text = "n/a"
            else:
                # Start a new chat session
                chat_session = model.start_chat(history=[])

                # Send the message with the page content to summarize
                prompt = f"""
                Please extract and summarize the following content. 

                Extract the address, contact number, and name, and return the information in the following JSON format:

                {{
                    "address": "<address>",
                    "contact_number": "<contact_number>",
                    "name": "<name>"
                }}

                If any of this information is not available or unclear, use "n/a" for that field.

                Content:

                "{page_content}"
                """
                retry_count = 0
                while retry_count < 5:  # Maximum of 5 retries
                    try:
                        response = chat_session.send_message(prompt)
                        response_text = response.text.strip()
                        break  # Exit the loop if the request is successful
                    except StopCandidateException as e:
                        print(f"Safety issue encountered for URL {url}: {e}")
                        response_text = "Safety issue, response not generated"
                        break
                    except ResourceExhausted as e:
                        retry_count += 1
                        wait_time = 2 ** retry_count  # Exponential backoff
                        print(f"Quota exceeded. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                        response_text = "Unexpected error, response not generated"
                        break

            # Append the result to the list
            results.append({
                "url": url,
                "response": response_text
            })

    # Write results to a new CSV file
    with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["url", "response"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"Responses saved to {output_csv_file}")

# Usage
csv_file_path = 'scraped_content_20240827_160123.csv'  # Path to your original CSV file
output_csv_file_path = 'summarized_content.csv'  # Path to the output CSV file

summarize_and_save_response(csv_file_path, output_csv_file_path)
