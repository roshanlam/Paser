# Parser
 
![Alt text](logo.webp)

A sophisticated web parsing tool designed to handle both static and dynamic web content efficiently. Built in Python, it utilizes a combination of BeautifulSoup for parsing HTML and Selenium for handling JavaScript-heavy webpages, making it versatile for a wide range of web crawling needs.


### Features
Multi-threaded Crawling: Leverages threading for efficient crawling of multiple URLs concurrently.
Dynamic Content Handling: Uses Selenium to parse content dynamically loaded by JavaScript.
HTML Parsing: Beautiful Soup is employed for easy and effective parsing of HTML content.
JSON Output: Extracted data is saved in a structured JSON format for easy integration and analysis.
Customizable: Can be tailored to specific crawling and parsing requirements.

### Setup

Clone the repository:
`git clone https://github.com/roshanlam/Parser.git`

Navigate to the project directory:
`cd Parser`

Install required packages:
`pip install -r requirements.txt`

### Usage

Add the URLs you want to crawl to links.txt, one URL per line.

Run the script:
`python main.py`


Check the `data` directory for parsed JSON results.