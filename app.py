import streamlit as st
import pandas as pd
import os
from scraper import WebScraper
import json
from datetime import datetime

class ScraperUI:
    def __init__(self):
        self.config_file = "scraper_config.json"
        self.load_sources()
        
    def load_sources(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.sources = json.load(f)
        else:
            self.sources = []
            
    def save_sources(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.sources, f)

    def run(self):
        st.title("Web Scraper Dashboard")
        
        # Sidebar for adding new sources
        with st.sidebar:
            st.header("Add New Source")
            new_url = st.text_input("URL")
            days_limit = st.number_input("Days to scrape (leave 0 for all)", min_value=0)
            if st.button("Add Source"):
                if new_url:
                    self.sources.append({
                        "url": new_url,
                        "days_limit": days_limit,
                        "last_scraped": None
                    })
                    self.save_sources()
                    st.success("Source added!")

        # Main area tabs
        tab1, tab2 = st.tabs(["Sources", "Library"])

        # Sources Tab
        with tab1:
            st.header("Configured Sources")
            for idx, source in enumerate(self.sources):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                with col1:
                    st.write(f"URL: {source['url']}")
                with col2:
                    st.write(f"Days: {source['days_limit'] or 'All'}")
                with col3:
                    if st.button("Scrape", key=f"scrape_{idx}"):
                        scraper = WebScraper(days_limit=source['days_limit'] if source['days_limit'] > 0 else None)
                        with col4:
                            progress_bar = st.progress(0)
                            result = scraper.scrape_url(source['url'], progress_callback=progress_bar.progress)
                        if result:
                            source['last_scraped'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            self.save_sources()
                            st.success("Scraped successfully!")
                        else:
                            st.error("Scraping failed!")

        # Library Tab
        with tab2:
            st.header("Scraped Content")
            if os.path.exists("scraped_data"):
                files = os.listdir("scraped_data")
                files = [f for f in files if f.endswith('.md')]
                
                for file in files:
                    with st.expander(file):
                        with open(os.path.join("scraped_data", file), 'r') as f:
                            content = f.read()
                            st.markdown(content)

if __name__ == "__main__":
    app = ScraperUI()
    app.run()