"""FastMCP server with tools for arithmetic, web content extraction, and doc search."""

import io
import zipfile
from typing import List

import minsearch
import requests
from fastmcp import FastMCP
from requests.exceptions import RequestException, Timeout

# Constants
DOCS_URL = "https://github.com/jlowin/fastmcp/archive/refs/heads/main.zip"

# Initialize FastMCP
mcp = FastMCP("Demo 🚀")

# Initialize Search Index
# We declare fields: text is 'content', filterable keyword is 'filename'
search_index = minsearch.Index(text_fields=["content"], keyword_fields=["filename"])


def initialize_search_index() -> None:
    """Download documentation and build the search index on startup."""
    print(f"📥 Downloading documentation from {DOCS_URL}...")
    try:
        response = requests.get(DOCS_URL, timeout=60)
        response.raise_for_status()

        documents = []

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for file_info in z.infolist():
                # Filter only markdown files
                if not (
                    file_info.filename.endswith(".md")
                    or file_info.filename.endswith(".mdx")
                ):
                    continue

                # Remove the top-level directory from the path
                # e.g., "fastmcp-main/docs/intro.md" -> "docs/intro.md"
                if "/" in file_info.filename:
                    clean_filename = file_info.filename.split("/", 1)[1]
                else:
                    clean_filename = file_info.filename

                # Skip directories or empty filenames
                if not clean_filename:
                    continue

                # Read and decode content
                text = z.read(file_info).decode("utf-8", errors="ignore")

                documents.append({"filename": clean_filename, "content": text})

        search_index.fit(documents)
        print(f"✅ Indexed {len(documents)} documents successfully.")

    except Exception as e:
        print(f"❌ Failed to initialize search index: {str(e)}")


@mcp.tool
def add(a: int, b: int) -> int:
    """
    Add two numbers.

    Args:
        a: First integer
        b: Second integer

    Returns:
        Sum of a and b
    """
    return a + b


@mcp.tool
def get_page_content(url: str, timeout: int = 30) -> str:
    """
    Get the content of the webpage as Markdown using Jina Reader.

    Args:
        url: The URL of the webpage to fetch
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Markdown-formatted content of the webpage or error message
    """
    # Validate URL format
    if not url.startswith(("http://", "https://")):
        return "Error: Invalid URL format. Must start with http:// or https://"

    # Jina Reader URL prefix
    jina_url = f"https://r.jina.ai/{url}"

    # Make the request with timeout
    try:
        response = requests.get(jina_url, timeout=timeout)
        response.raise_for_status()
        return response.text
    except Timeout:
        return f"Error: Request timed out after {timeout} seconds"
    except RequestException as e:
        return f"Error fetching content: {str(e)}"


@mcp.tool
def search_documentation(query: str) -> List[str]:
    """
    Search the FastMCP documentation for specific topics.

    Args:
        query: The search term or question (e.g., "how to use context")

    Returns:
        A list of matching document snippets with source filenames.
    """
    results = search_index.search(query=query, boost={"content": 1}, num_results=5)

    output = []
    for res in results:
        # Format the output for clarity for the AI client
        formatted_result = (
            f"--- SOURCE: {res['filename']} ---\n"
            f"{res['content'][:1500]}..."  # Truncate slightly to avoid huge context loads
        )
        output.append(formatted_result)

    return output


if __name__ == "__main__":
    # Initialize the data before running the server
    initialize_search_index()
    mcp.run()
