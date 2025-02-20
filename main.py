from scraper import WebScraper
import time
import argparse

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Web scraper with configurable parameters')
    parser.add_argument('--depth', type=int, default=2, help='Maximum depth for recursive scraping')
    parser.add_argument('--days', type=int, default=7, help='Number of days to limit scraping (0 for no limit)')
    parser.add_argument('--wait', type=int, default=2, help='Wait time between requests in seconds')
    args = parser.parse_args()

    # Create scraper instance with configured parameters
    scraper = WebScraper(days_limit=args.days if args.days > 0 else None)
    
    urls = [
        "https://example.com/forum/post1",
        "https://example.com/forum/post2",
        # Add your forum URLs here
    ]
    
    for url in urls:
        print(f"Scraping {url}...")
        filepath = scraper.scrape_url(url, max_depth=args.depth)
        if filepath:
            print(f"Successfully saved to {filepath}")
        else:
            print(f"Failed to scrape or skipped {url}")
        time.sleep(args.wait)  # Add a configurable delay between requests

if __name__ == "__main__":
    main()