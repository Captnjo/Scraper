from scraper import WebScraper
import time

def main():
    # Create scraper instance with 7-day limit
    scraper = WebScraper(days_limit=7)
    
    urls = [
        "https://example.com/forum/post1",
        "https://example.com/forum/post2",
        # Add your forum URLs here
    ]
    
    for url in urls:
        print(f"Scraping {url}...")
        filepath = scraper.scrape_url(url)
        if filepath:
            print(f"Successfully saved to {filepath}")
        else:
            print(f"Failed to scrape or skipped {url}")
        time.sleep(2)  # Add a delay between requests

if __name__ == "__main__":
    main()