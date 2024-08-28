Web Content Extraction Script

This Python script extracts visible text content from a list of websites provided in a CSV file and saves the results to a new CSV file. It also logs the extraction process, including any errors encountered, into a log file.

Prerequisites

	•	Python 3.x (I used 3.8)
	•	Required Python Packages:
	•	pandas
	•	requests
	•	beautifulsoup4

Installation

You can install the required Python packages using pip: 
    
    pip install pandas requests beautifulsoup4

Script Overview

Functionality
	1.	CSV Input Handling:
	•	The script reads a CSV file (100lines.csv) containing website URLs in a column named website.
	•	It performs error handling to ensure the CSV is read correctly and that the website column exists.
	2.	Web Scraping:
	•	The script sends an HTTP GET request to each URL to retrieve the page content.
	•	The visible text content of each page is extracted using BeautifulSoup and stored in a list.
	3.	Error Logging:
	•	Any errors encountered during the HTTP request (e.g., timeouts, connection errors) are logged to a log file.
	•	The log file is created with a timestamp to avoid overwriting previous logs.
	4.	Output:
	•	The extracted page content and any errors are saved to a new CSV file with a timestamped filename.
	•	The CSV file uses QUOTE_NONNUMERIC quoting to handle potential issues with commas in the text.

Files Generated
	•	Log File:
	•	A log file (scrape_log_YYYYMMDD_HHMMSS.log) is created, containing details of the scraping process, including any errors.
	•	Extracted Content CSV:
	•	A CSV file (scraped_content_YYYYMMDD_HHMMSS.csv) is generated, containing the following columns:
	•	url: The URL of the website.
	•	page_content: The visible text content extracted from the website.
	•	error: Any errors encountered during the request (or None if successful).

Code Structure
	•	extract_page_content(url) Function:
	•	Sends a GET request to the provided URL.
	•	Extracts and returns the visible text content from the page.
	•	Handles and logs any request-related errors.
	•	Main Script:
	•	Reads the input CSV file.
	•	Iterates through the URLs, calling extract_page_content() for each.
	•	Logs the results to a file and saves the extracted content to a new CSV file.

Usage

    python your_script_name.py

License

This project is licensed under the MIT License. See the LICENSE file for details.

Note: Ensure that the input CSV is formatted correctly and that your environment has the necessary permissions for making HTTP requests.

	1.	Prepare the Input CSV:
	•	Ensure your CSV file (100lines.csv) has a column named website with the URLs you want to scrape.
	2.	Run the Script:
	•	Execute the script using Python:
