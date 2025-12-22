"""Module for scraping and analyzing word count from a webpage."""

from main import get_page_content

# 1. Use the MCP tool we created to scrape the site
url = "https://datatalks.club/"
try:
    content = get_page_content(url)
    if not content:
        print(f"Error: No content retrieved from {url}")
        exit(1)
except Exception as e:
    print(f"Error fetching content from {url}: {e}")
    exit(1)
# 2. "AI Agent Logic" - Count the specific word
# Converting to lower case because "Data" and "data" usually both count
# when an AI reads text.
count = content.lower().count("data")

print(f"Total count of 'data': {count}")
