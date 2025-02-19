# Web Scraper with Streamlit UI

A powerful and flexible web scraping tool that supports both single pages and forum content scraping, featuring an intuitive Streamlit interface and advanced content processing capabilities.

## Features

- Single page scraping with automatic content extraction
- Forum post scraping with recursive capabilities
- Smart content filtering and processing
- Progress tracking with real-time updates
- Clean Markdown output format
- User-friendly Streamlit interface
- Configurable scraping parameters
- Automatic metadata extraction (source URL, timestamp)
- Periodic scraping with customizable schedules
- Enhanced content filtering with custom rules
- Configurable output directory structure

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

Launch the Streamlit interface:
```bash
streamlit run app.py
```

The interface provides:

- **Sources Management**: Configure and manage scraping URLs
- **Library**: Browse, search, and download scraped content
- **Settings**: Customize scraping parameters
  - Time limits for content retrieval
  - Recursive depth for forum scraping
  - Content filtering options with custom rules
  - Output format preferences
  - Periodic scraping schedules
  - Custom output directory configuration

## Content Processing

- Automatic content extraction and cleaning
- Metadata preservation (source URL, timestamp)
- Structured output in Markdown format
- Smart duplicate detection
- Error handling and retry mechanisms

## Output

Scraped content is saved in the `scraped_data` directory in markdown format, following the naming convention:
`domain_timestamp.md`

Example output structure:
```
scraped_data/
  ├── example.com_20250219_112559.md
  └── forum.com_20250219_113022.md
```

## Requirements

- Python 3.9+
- Chrome/Chromium browser
- Required Python packages (specified in requirements.txt)

## Error Handling

- Automatic retry for failed requests
- Detailed error logging
- Graceful failure recovery
- Session persistence

## Performance

- Efficient memory usage
- Concurrent scraping capabilities
- Rate limiting to respect server limits
- Progress tracking for long-running operations
