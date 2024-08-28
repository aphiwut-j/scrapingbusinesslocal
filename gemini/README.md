Content Summarization using Gemini API

This Python script processes content from a CSV file, sends the content to the Gemini API to extract and summarize specific information, and saves the results to a new CSV file. The API provides a structured summary in JSON format, extracting the address, contact number, and name from the provided content.

Prerequisites

	•	Python 3.x (I used 3.8)
 
	•	Google Gemini API Key

Required Python Packages

Install the required Python packages using pip: 
  pip install google-generativeai

Environment Setup

Before running the script, you need to set up your environment:

API Key:

	•	Obtain your Google Gemini API key.
 
	•	Set it as an environment variable: export API_KEY='your_gemini_api_key'

Script Overview

Key Components

GenerativeModel Configuration:

•	Configures the Gemini API model with specific parameters such as temperature, top_p, top_k, and max_output_tokens.

CSV Processing:

•	The script reads a CSV file containing URLs, page content, and error statuses.

•	It skips rows where the content is marked as ‘N/A’ or if an error occurred.

Content Summarization:

•	For each row of valid content, the script starts a new chat session with the Gemini API.

•	It sends the content with a prompt requesting a summary in JSON format.

Error Handling:

•	The script includes robust error handling, including retries with exponential backoff for quota-related issues.

Output:

•	The results are saved in a new CSV file with the URL and the summarized response.

Script Usage
Prepare Your CSV File:
•	Ensure your CSV file has columns named url, page_content, and error.

Run the Script:

•	Update the csv_file_path and output_csv_file_path variables with the paths to your input and output CSV files.

•	Run the script:
 python your_script_name.py

Functions
	•	summarize_and_save_response(csv_file, output_csv_file):
	•	Reads the input CSV file.
	•	Processes each row to generate a summary using the Gemini API.
	•	Writes the summarized responses to the output CSV file.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Note: Ensure that the environment variable API_KEY is correctly set before running the script. The script handles errors and retries if the API quota is exceeded, but you should monitor for any issues related to API limits.
