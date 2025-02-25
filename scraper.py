import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import platform

class WebScraper:
    def __init__(self, output_dir="scraped_data", days_limit=7):
        self.output_dir = output_dir
        self.days_limit = days_limit
        self.cutoff_date = datetime.now() - timedelta(days=days_limit) if days_limit else None
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Setup Selenium with robust error handling
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in headless mode
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Add additional Chrome options for stability
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-notifications")
            
            # Try to locate Chrome binary
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome Beta",  # macOS Beta
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome Canary",  # macOS Canary
                "/usr/bin/google-chrome",  # Linux
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",  # Windows
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"  # Windows x86
            ]
            
            chrome_binary = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary = path
                    print(f"Found Chrome binary at: {path}")
                    break
                    
            if chrome_binary:
                chrome_options.binary_location = chrome_binary
            else:
                print("Warning: Chrome browser not found in standard locations.")
                print("Attempting to continue without specifying binary location...")
            
            # Set up Chrome WebDriver using Selenium Manager
            service = Service()
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(30)
            print("Chrome WebDriver initialized successfully")
                
        except Exception as e:
            print(f"Failed to initialize Chrome WebDriver: {str(e)}")
            print("Please ensure Chrome browser is installed and up to date.")
            print("You may need to manually install ChromeDriver or update Chrome.")
            self.driver = None
        except Exception as e:
            print(f"Error setting up Chrome options: {str(e)}")
            self.driver = None
    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def _is_valid_link(self, link, base_url):
        """Check if a link should be followed based on various criteria."""
        try:
            parsed_link = urlparse(link)
            parsed_base = urlparse(base_url)
            
            # Check if the link is from the same domain
            if parsed_link.netloc != parsed_base.netloc:
                return False
            
            # Ignore common file types that aren't likely to contain content
            ignored_extensions = ('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.pdf')
            if any(parsed_link.path.endswith(ext) for ext in ignored_extensions):
                return False
            
            # Ignore common non-content paths
            ignored_paths = ('login', 'logout', 'signup', 'register', 'search')
            path_parts = parsed_link.path.strip('/').split('/')
            if any(part in ignored_paths for part in path_parts):
                return False
            
            return True
            
        except Exception:
            return False

    def scrape_url(self, url, progress_callback=None, depth=1, max_depth=2, visited_urls=None):
        if visited_urls is None:
            visited_urls = set()
        
        if depth > max_depth or url in visited_urls:
            return None
            
        visited_urls.add(url)
        
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
            
            # Extract all links from the page
            all_links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if not href.startswith('http'):
                    href = url + href if href.startswith('/') else url + '/' + href
                if self._is_valid_link(href, url):
                    all_links.append(href)
            
            # Check if this is a forum main page
            post_links = self.extract_post_links(soup, url)
            all_links.extend(post_links)
            
            if all_links and depth < max_depth:
                print(f"Found {len(all_links)} links to scrape at depth {depth}")
                scraped_files = []
                
                for idx, link_url in enumerate(all_links):
                    if link_url not in visited_urls:
                        if progress_callback:
                            progress = 0.2 + (0.8 * (idx / len(all_links)))
                            progress_callback(progress)
                        
                        print(f"Scraping link {idx+1}/{len(all_links)}: {link_url}")
                        result = self.scrape_url(link_url, progress_callback=None, depth=depth+1, max_depth=max_depth, visited_urls=visited_urls)
                        if result:
                            scraped_files.append(result)
                
                if progress_callback:
                    progress_callback(1.0)
                
                return scraped_files[0] if scraped_files else None
            
            else:
                # Handle single page content
                title = soup.title.string if soup.title else "Untitled"
            
                # Try to find the main article content using common article selectors
                main_content = None
                content_selectors = [
                    {'tag': 'article'},
                    {'tag': 'main'},
                    {'tag': 'div', 'class_': 'article-content'},
                    {'tag': 'div', 'class_': 'post-content'},
                    {'tag': 'div', 'class_': 'entry-content'},
                    {'tag': 'div', 'id': 'article-body'},
                    {'tag': 'div', 'class_': 'content'},
                    {'tag': 'div', 'id': 'content'}
                ]

                for selector in content_selectors:
                    if 'class_' in selector:
                        main_content = soup.find(selector['tag'], class_=selector['class_'])
                    elif 'id' in selector:
                        main_content = soup.find(selector['tag'], id=selector['id'])
                    else:
                        main_content = soup.find(selector['tag'])
                    
                    if main_content:
                        break

                # If no specific content area found, fall back to body but try to clean it
                if not main_content:
                    main_content = soup.find('body')
                    if main_content:
                        # Remove common non-content elements
                        for element in main_content.find_all(['nav', 'header', 'footer', 'aside', 'script', 'style', 'iframe']):
                            element.decompose()
                        
                        # Remove elements with common ad-related classes or IDs
                        ad_indicators = ['ad', 'advertisement', 'banner', 'sidebar', 'popup', 'modal', 'newsletter']
                        for indicator in ad_indicators:
                            for element in main_content.find_all(class_=lambda x: x and indicator in x.lower()):
                                element.decompose()
                            for element in main_content.find_all(id=lambda x: x and indicator in x.lower()):
                                element.decompose()
            
                markdown_content = f"# {title}\n\n"
                markdown_content += f"Source: {url}\n"
                markdown_content += f"Date scraped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                if main_content:
                    # Extract text from content elements, maintaining hierarchy
                    for element in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
                        text = element.get_text().strip()
                        if text and len(text) > 20:  # Filter out very short snippets
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

    def extract_post_links(self, soup, base_url):
        """Extract forum post links from a page.
        Args:
            soup (BeautifulSoup): The parsed HTML content
            base_url (str): The base URL of the page
        Returns:
            list: List of extracted post URLs
        """
        post_links = []
        
        # Common forum post link patterns
        post_indicators = [
            {'tag': 'div', 'class_': 'post'},
            {'tag': 'div', 'class_': 'thread'},
            {'tag': 'div', 'class_': 'topic'},
            {'tag': 'article', 'class_': 'forum-post'},
            {'tag': 'div', 'class_': 'message'},
            {'tag': 'div', 'class_': 'discussion'}
        ]
        
        # Look for links within elements that match forum post patterns
        for indicator in post_indicators:
            elements = soup.find_all(indicator['tag'], class_=indicator.get('class_'))
            for element in elements:
                links = element.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if not href.startswith('http'):
                        href = base_url + href if href.startswith('/') else base_url + '/' + href
                    if self._is_valid_link(href, base_url):
                        post_links.append(href)
        
        # Also look for links with common forum URL patterns
        forum_patterns = ['topic', 'thread', 'discussion', 'post', 'forum']
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(pattern in href.lower() for pattern in forum_patterns):
                if not href.startswith('http'):
                    href = base_url + href if href.startswith('/') else base_url + '/' + href
                if self._is_valid_link(href, base_url):
                    post_links.append(href)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(post_links))