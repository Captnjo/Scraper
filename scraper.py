import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class WebScraper:
    def __init__(self, output_dir="scraped_data", days_limit=7):
        self.output_dir = output_dir
        self.days_limit = days_limit
        self.cutoff_date = datetime.now() - timedelta(days=days_limit) if days_limit else None
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Setup Selenium with simplified Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error initializing Chrome driver: {str(e)}")
            self.driver = None

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def scrape_url(self, url, progress_callback=None):
        if self.driver is None:
            print("Chrome driver not initialized properly")
            return None
            
        try:
            if progress_callback:
                progress_callback(0.1)  # Started loading page
                
            self.driver.get(url)
            time.sleep(5)  # Wait for JavaScript content to load
            
            if progress_callback:
                progress_callback(0.3)  # Page loaded
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            if progress_callback:
                progress_callback(0.5)  # Parsing started
            
            title = soup.title.string if soup.title else "Untitled"
            
            # Try different content selectors
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_='content') or
                soup.find('div', id='content') or
                soup.find('body')
            )
            
            markdown_content = f"# {title}\n\n"
            markdown_content += f"Source: {url}\n"
            markdown_content += f"Date scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if main_content:
                # Extract text from common content elements
                for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span']):
                    text = element.get_text().strip()
                    if text:  # Only add non-empty text
                        if element.name.startswith('h'):
                            markdown_content += f"\n{'#' * int(element.name[1:])} {text}\n"
                        else:
                            markdown_content += f"\n{text}\n"
            
            domain = urlparse(url).netloc
            filename = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = os.path.join(self.output_dir, filename)
            
            if progress_callback:
                progress_callback(0.8)  # Content extracted
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            if progress_callback:
                progress_callback(1.0)  # Complete
                
            return filepath
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            if progress_callback:
                progress_callback(0.0)  # Reset on error
            return None