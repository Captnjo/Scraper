# Web Scraper with Streamlit UI

A web scraping tool that supports both single pages and forum content scraping, with a user-friendly Streamlit interface.

## Features

- Single page scraping
- Forum post scraping with recursive capabilities
- Progress tracking
- Markdown output format
- Streamlit-based user interface

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the Streamlit interface:
```bash
streamlit run app.py
```

The interface provides:

- Sources management tab for URL configuration
- Library tab for viewing and downloading scraped content
- Settings tab for advanced scraping options
- Progress tracking during scraping
- Configurable time limits for content

## Output
Scraped content is saved in the `scraped_data` directory in markdown format, with the following naming convention: `domain_timestamp.md`

## Requirements
- Python 3.9+
- Chrome/Chromium browser
- Required Python packages listed in requirements.txt
