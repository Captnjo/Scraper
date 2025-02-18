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

    def extract_post_links(self, soup, base_url):
        links = []
        # Look for topic links in the forum
        for topic in soup.find_all('tr', class_='topic-list-item'):
            link = topic.find('a', class_='title')
            if link and link.get('href'):
                href = link['href']
                if not href.startswith('http'):
                    href = base_url + href if href.startswith('/') else base_url + '/' + href
                links.append(href)
        return list(set(links))  # Remove duplicates

    def scrape_url(self, url, progress_callback=None):
        if self.driver is None:
            print("Chrome driver not initialized properly")
            return None
            
        try:
            if progress_callback:
                progress_callback(0.1)

            self.driver.get(url)
            time.sleep(5)
            
            if progress_callback:
                progress_callback(0.2)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Check if this is a forum main page
            post_links = self.extract_post_links(soup, url)
            
            if post_links:
                print(f"Found {len(post_links)} posts to scrape")
                scraped_files = []
                
                for idx, post_url in enumerate(post_links):
                    if progress_callback:
                        progress = 0.2 + (0.8 * (idx / len(post_links)))
                        progress_callback(progress)
                        
                    print(f"Scraping post {idx+1}/{len(post_links)}: {post_url}")
                    
                    self.driver.get(post_url)
                    time.sleep(3)
                    
                    post_source = self.driver.page_source
                    post_soup = BeautifulSoup(post_source, 'html.parser')
                    
                    # Extract post content with specific forum structure
                    title = post_soup.find('h1', class_='topic-title')
                    title = title.get_text().strip() if title else "Untitled"
                    
                    main_content = post_soup.find('div', class_='topic-body')
                    
                    markdown_content = f"# {title}\n\n"
                    markdown_content += f"Source: {post_url}\n"
                    markdown_content += f"Date scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    
                    if main_content:
                        for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'code']):
                            text = element.get_text().strip()
                            if text:
                                if element.name.startswith('h'):
                                    markdown_content += f"\n{'#' * int(element.name[1:])} {text}\n"
                                elif element.name in ['pre', 'code']:
                                    markdown_content += f"\n```\n{text}\n```\n"
                                else:
                                    markdown_content += f"\n{text}\n"
                    
                    domain = urlparse(post_url).netloc
                    filename = f"{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    
                    scraped_files.append(filepath)
                
                if progress_callback:
                    progress_callback(1.0)
                    
                return scraped_files[0] if scraped_files else None
            
            else:
                # Handle single page as before
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
                progress_callback(0.0)
            return None