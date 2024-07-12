import requests
from bs4 import BeautifulSoup
import sqlite3
from config import logger, TAG_DELIMITER


def fetch_page_title(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else 'No Title Found'
            return title
        else:
            logger.error(f"Failed to fetch page: HTTP {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

