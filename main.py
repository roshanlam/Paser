import requests
import json
import os
import threading
from queue import Queue
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Constants
INPUT_FILE = 'links.txt'
OUTPUT_DIR = 'data'
NUMBER_OF_THREADS = 8

# Queue and Directory Setup
queue = Queue()
create_dir(OUTPUT_DIR)

# Create Directory


def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Write JSON Data to File


def write_json(file_name, data):
    with open(file_name, 'w') as f:
        json.dump(data, f)

# Convert File to Set of URLs


def file_to_set(file_name):
    results = set()
    with open(file_name, 'rt') as f:
        for line in f:
            results.add(line.replace('\n', ''))
    return results

# Tag Class for HTML Elements


class Tag:
    def __init__(self, name):
        self.name = name
        self.content = None
        self.attributes = {}

    def add_content(self, text):
        self.content = ' '.join(text.split())

    def add_attribute(self, key, value):
        if str(type(value)) == "<class 'str'>" and len(value) > 0:
            self.attributes[key] = value

    def get_data(self):
        return {
            'name': self.name,
            'content': self.content,
            'attributes': self.attributes if self.attributes else None
        }

# Domain Class for URL Parsing


class Domain:
    def __init__(self, url):
        self.url = url
        self.domain = self.get_domain()
        self.sub_domain = self.get_sub_domain()

    def get_domain(self):
        try:
            return '.'.join(self.get_sub_domain().split('.')[-2:])
        except IndexError:
            return ''

    def get_sub_domain(self):
        return urlparse(self.url).netloc

# ResponseParser Class


class ResponseParser:
    def __init__(self, response):
        self.response = response
        self.headers = self.parse_headers()

    def parse_headers(self):
        header_dict = {}
        for line in str(self.response.info()).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                header_dict[key.strip()] = value.strip()
        return header_dict

# PageParser Class


class PageParser:
    def __init__(self, html_string):
        self.soup = BeautifulSoup(html_string, 'html.parser')
        self.all_tags = self.parse()

    def parse(self):
        tags = []
        for tag in self.soup.find_all():
            t = Tag(tag.name)
            if tag.string:
                t.add_content(tag.string)
            for attr, value in tag.attrs.items():
                t.add_attribute(attr, value)
            tags.append(t.get_data())
        return tags

# MasterParser Class


class MasterParser:
    @staticmethod
    def parse(url, output_dir, output_file):
        try:
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req) as resp:
                resp_parser = ResponseParser(resp)
                page_parser = PageParser(resp.read().decode('utf-8'))
                json_results = {
                    'url': url,
                    'status': resp.getcode(),
                    'headers': resp_parser.headers,
                    'tags': page_parser.all_tags
                }
                write_json(os.path.join(
                    output_dir, f'{output_file}.json'), json_results)
        except Exception as e:
            print(f"Error parsing {url}: {e}")

    @staticmethod
    def parse_dynamic(url, output_dir, output_file):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=chrome_options)
        try:
            driver.get(url)
            page_parser = PageParser(driver.page_source)
            json_results = {
                'url': url,
                'status': 200,
                'tags': page_parser.all_tags
            }
            write_json(os.path.join(
                output_dir, f'{output_file}.json'), json_results)
        except Exception as e:
            print(f"Error parsing dynamic content of {url}: {e}")
        finally:
            driver.quit()


def is_page_dynamic(url):
    """
    Attempts to determine if the webpage at the given URL is dynamic.
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            return False  # Can't determine if non-200 response

        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for a large number of script tags
        scripts = soup.find_all('script')
        if len(scripts) > 5:  # Arbitrary threshold
            return True

        # Check for minimal body content
        body_text = soup.find('body').get_text(strip=True)
        if len(body_text) < 50:  # Arbitrary threshold
            return True

        # Other heuristics can be added here

    except requests.RequestException as e:
        print(f"Error checking URL {url}: {e}")
        return False

    return False


# Worker Thread Function
def work():
    while True:
        url = queue.get()
        if is_page_dynamic(url):  # Replace with actual logic to determine if URL is dynamic
            MasterParser.parse_dynamic(url, OUTPUT_DIR, str(queue.qsize()))
        else:
            MasterParser.parse(url, OUTPUT_DIR, str(queue.qsize()))
        queue.task_done()

# Create Worker Threads


def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()

# Create Jobs from URLs


def create_jobs():
    for url in file_to_set(INPUT_FILE):
        queue.put(url)
    queue.join()


# Main Execution
if __name__ == "__main__":
    create_dir(OUTPUT_DIR)
    create_workers()
    create_jobs()
