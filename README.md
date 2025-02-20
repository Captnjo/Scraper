# Web Scraper

A powerful and flexible web scraping tool that supports both single pages and forum content scraping, featuring an intuitive Streamlit interface and command-line usage for automation needs.

## Features

- Single page scraping with automatic content extraction
- Forum post scraping with recursive capabilities
- Smart content filtering and processing
- Progress tracking with real-time updates
- Clean Markdown output format
- Configurable scraping parameters
- Automatic metadata extraction (source URL, timestamp)
- Periodic scraping with customizable schedules
- Enhanced content filtering with custom rules
- Configurable output directory structure

## Requirements

- Python 3.9+
- Chrome/Chromium browser
- Required Python packages (specified in requirements.txt)

## Streamlit Interface

The Streamlit interface provides a user-friendly way to manage and monitor scraping tasks.

### Starting the Interface

Launch the Streamlit interface with:
```bash
streamlit run app.py
```

### Features

- **Sources Management**
  - Add and manage scraping URLs
  - Configure scraping intervals
  - Set content age limits

- **Library**
  - Browse scraped content
  - Search through collected data
  - Download content in Markdown format

- **Settings**
  - Time limits for content retrieval
  - Recursive depth for forum scraping
  - Content filtering options
  - Output format preferences
  - Periodic scraping schedules
  - Custom output directory configuration

## Command Line Interface

The command-line interface is ideal for automation and scripting needs.

### Usage

```bash
python main.py [options]
```

### Options

- `--depth DEPTH`: Maximum depth for recursive scraping (default: 2)
- `--days DAYS`: Number of days to limit scraping (default: 7, 0 for no limit)
- `--wait WAIT`: Wait time between requests in seconds (default: 2)

### Example

```bash
# Scrape with default settings
python main.py

# Scrape with custom settings
python main.py --depth 3 --days 14 --wait 5
```

## Performance

- Efficient memory usage
- Concurrent scraping capabilities
- Rate limiting to respect server limits
- Progress tracking for long-running operations

## Output

Scraped content is saved in Markdown format with:
- Clear content hierarchy
- Source URL and timestamp
- Cleaned and formatted text
- Organized file structure

## Note

Please use this tool responsibly and in accordance with the terms of service of the websites you're scraping.
