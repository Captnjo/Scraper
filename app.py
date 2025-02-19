import streamlit as st
import pandas as pd
import os
from scraper import WebScraper
import json
from datetime import datetime, timedelta
import time
import threading
import schedule


class ScraperUI:
    def __init__(self):
        self.config_file = "scraper_config.json"
        self.load_sources()
        self.scheduler = None
        self.start_scheduler()
        
    def load_sources(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.sources = json.load(f)
        else:
            self.sources = []
            
    def save_sources(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.sources, f)

    def start_scheduler(self):
        if self.scheduler is None:
            self.scheduler = threading.Thread(target=self.run_scheduler, daemon=True)
            self.scheduler.start()

    def run_scheduler(self):
        while True:
            self.check_and_scrape_sources()
            time.sleep(60)  # Check every minute

    def check_and_scrape_sources(self):
        current_time = datetime.now()
        for source in self.sources:
            if 'interval_hours' not in source or not source['interval_hours']:
                continue

            last_scraped = datetime.strptime(source['last_scraped'], '%Y-%m-%d %H:%M:%S') if source['last_scraped'] else None
            if last_scraped is None or current_time - last_scraped >= timedelta(hours=source['interval_hours']):
                # Load scraper settings
                settings = {}
                if os.path.exists("scraper_settings.json"):
                    with open("scraper_settings.json", 'r') as f:
                        settings = json.load(f)

                scraper = WebScraper(days_limit=source['days_limit'] if source['days_limit'] > 0 else None)
                max_depth = settings.get('max_depth', 2) if settings.get('follow_links', False) else 1
                result = scraper.scrape_url(source['url'], max_depth=max_depth)

                if result:
                    source['last_scraped'] = current_time.strftime('%Y-%m-%d %H:%M:%S')
                    self.save_sources()

    def run(self):
        st.title("Web Scraper Dashboard")
        
        # Sidebar with configuration
        with st.sidebar:
            st.header("Settings")
            wait_time = st.slider("Page Load Wait Time", 1, 10, 5, 
                help="Seconds to wait for page loading")
            
            st.header("Add New Source")
            new_url = st.text_input("URL")
            days_limit = st.number_input("Days to scrape (leave 0 for all)", min_value=0)
            interval_hours = st.number_input("Scraping Interval (hours, 0 for manual only)", 
                min_value=0, value=0, help="How often to automatically scrape this source")
            if st.button("Add Source"):
                if new_url:
                    self.sources.append({
                        "url": new_url,
                        "days_limit": days_limit,
                        "interval_hours": interval_hours,
                        "last_scraped": None
                    })
                    self.save_sources()
                    st.success("Source added!")

        # Main area tabs
        tab1, tab2, tab3 = st.tabs(["Sources", "Library", "Settings"])

        # Sources Tab
        with tab1:
            st.header("Configured Sources")
            if not self.sources:
                st.info("No sources configured yet. Add some from the sidebar!")
            
            for idx, source in enumerate(self.sources):
                with st.expander(f"Source: {source['url']}", expanded=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"Days Limit: {source['days_limit'] or 'All'}")
                        st.write(f"Scraping Interval: {source['interval_hours']} hours" if source.get('interval_hours', 0) > 0 else "Manual scraping only")
                        if source['last_scraped']:
                            st.write(f"Last Scraped: {source['last_scraped']}")
                            if source.get('interval_hours', 0) > 0:
                                last_scraped = datetime.strptime(source['last_scraped'], '%Y-%m-%d %H:%M:%S')
                                next_scrape = last_scraped + timedelta(hours=source['interval_hours'])
                                st.write(f"Next Scheduled: {next_scrape.strftime('%Y-%m-%d %H:%M:%S')}")
                    with col2:
                        if st.button("Scrape", key=f"scrape_{idx}"):
                            # Load scraper settings
                            settings = {}
                            if os.path.exists("scraper_settings.json"):
                                with open("scraper_settings.json", 'r') as f:
                                    settings = json.load(f)
                                
                            scraper = WebScraper(days_limit=source['days_limit'] if source['days_limit'] > 0 else None)
                            progress_bar = st.progress(0)
                            status = st.empty()
                            
                            def update_progress(progress):
                                progress_bar.progress(progress)
                                if progress < 1.0:
                                    status.text(f"Scraping... {progress*100:.0f}%")
                                else:
                                    status.text("Complete!")
                                    
                            # Use settings for recursive scraping
                            max_depth = settings.get('max_depth', 2) if settings.get('follow_links', False) else 1
                            result = scraper.scrape_url(
                                source['url'], 
                                progress_callback=update_progress,
                                max_depth=max_depth
                            )
                            
                            if result:
                                source['last_scraped'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                self.save_sources()
                                st.success("Scraped successfully!")
                            else:
                                st.error("Scraping failed!")
                    with col3:
                        if st.button("Remove", key=f"remove_{idx}"):
                            self.sources.pop(idx)
                            self.save_sources()
                            st.experimental_rerun()

        # Library Tab
        with tab2:
            st.header("Scraped Content")
            if os.path.exists("scraped_data"):
                files = sorted(os.listdir("scraped_data"), reverse=True)
                files = [f for f in files if f.endswith('.md')]
                
                if not files:
                    st.info("No scraped content yet!")
                    
                for file in files:
                    with st.expander(f"{file} ({time.ctime(os.path.getctime(os.path.join('scraped_data', file)))})"):
                        with open(os.path.join("scraped_data", file), 'r') as f:
                            content = f.read()
                            st.markdown(content)
                            st.download_button(
                                "Download",
                                content,
                                file_name=file,
                                mime="text/markdown",
                                key=f"download_{file}"
                            )
        
        # Settings Tab
        with tab3:
            st.header("Scraper Settings")
            
            # Load current settings
            settings = {}
            if os.path.exists("scraper_settings.json"):
                with open("scraper_settings.json", 'r') as f:
                    settings = json.load(f)
            
            # Output Directory Configuration
            output_dir = st.text_input(
                "Output Directory",
                value=settings.get('output_dir', 'scraped_data'),
                help="Directory where scraped data will be saved. Use absolute or relative path."
            )
            
            # Create directory if it doesn't exist when path is changed
            if output_dir != settings.get('output_dir'):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    settings['output_dir'] = output_dir
                    with open("scraper_settings.json", 'w') as f:
                        json.dump(settings, f)
                    st.success(f"Directory '{output_dir}' is ready for use")
                except Exception as e:
                    st.error(f"Failed to create directory: {str(e)}")

            # Save settings
            if st.button("Save Settings", key="save_output_dir"):
                settings['output_dir'] = output_dir
                # Create directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)
                with open("scraper_settings.json", 'w') as f:
                    json.dump(settings, f)
                st.success("Settings saved successfully!")
            st.header("Advanced Settings")
            enable_js = st.checkbox("Enable JavaScript", value=True, 
                help="Enable JavaScript processing (required for dynamic content)")
            follow_links = st.checkbox("Follow Links", value=False, 
                help="Follow and scrape linked pages (for forum posts)")
            max_depth = st.number_input("Max Depth", min_value=1, max_value=10, value=2,
                help="Maximum depth for following links")
            
            # Add link filtering options
            st.subheader("Link Filtering")
            filter_same_domain = st.checkbox("Stay on Same Domain", value=True,
                help="Only follow links from the same domain as the source URL")
            ignored_paths = st.text_input("Ignored Paths (comma-separated)",
                value="login,logout,signup,register,search",
                help="Paths to ignore when following links")
            ignored_extensions = st.text_input("Ignored File Extensions (comma-separated)",
                value=".css,.js,.png,.jpg,.jpeg,.gif,.pdf",
                help="File extensions to ignore when following links")
    
            # Save settings when changed
            if st.button("Save Settings", key="save_advanced_settings"):
                settings = {
                    "enable_js": enable_js,
                    "follow_links": follow_links,
                    "max_depth": max_depth,
                    "filter_same_domain": filter_same_domain,
                    "ignored_paths": ignored_paths.split(','),
                    "ignored_extensions": ignored_extensions.split(',')
                }
                with open("scraper_settings.json", 'w') as f:
                    json.dump(settings, f)
                st.success("Settings saved!")

if __name__ == "__main__":
    app = ScraperUI()
    app.run()