"""FastMCP server with tools for arithmetic, web content extraction, and doc search."""

import io
import ipaddress
import socket
import zipfile
from typing import List, Set
from urllib.parse import urlparse

import minsearch
import requests
from fastmcp import FastMCP
from requests.exceptions import RequestException, Timeout

# Constants
DOCS_URL = "https://github.com/jlowin/fastmcp/archive/refs/heads/main.zip"

# Configurable allowlist for safe domains (empty by default)
ALLOWED_DOMAINS: Set[str] = set()
# Example: ALLOWED_DOMAINS = {"example.com", "trusted-site.org"}

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
        raise


def is_safe_url(url: str) -> tuple[bool, str]:
    """
    Validate URL to prevent SSRF attacks by blocking requests to internal/private addresses.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_safe: bool, error_message: str)
        If safe, error_message is empty. If unsafe, contains reason for rejection.
    """
    try:
        # Parse the URL
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            return False, "Error: Unable to extract hostname from URL"

        # Check if domain is in allowlist
        if ALLOWED_DOMAINS and hostname in ALLOWED_DOMAINS:
            return True, ""

        # Block localhost variations
        localhost_names = {"localhost", "localhost.localdomain"}
        if hostname.lower() in localhost_names:
            return False, "Error: Access to localhost is not permitted"

        try:
            # Resolve hostname to IP addresses
            addr_info = socket.getaddrinfo(hostname, None)
            ip_addresses = {info[4][0] for info in addr_info}
        except socket.gaierror:
            return False, f"Error: Unable to resolve hostname '{hostname}'"

        # Check each resolved IP address
        for ip_str in ip_addresses:
            try:
                ip = ipaddress.ip_address(ip_str)

                # Check for various unsafe IP ranges
                if ip.is_loopback:
                    return False, f"Error: Loopback address ({ip_str}) is not permitted"

                if ip.is_private:
                    return False, f"Error: Private address ({ip_str}) is not permitted"

                if ip.is_link_local:
                    return (
                        False,
                        f"Error: Link-local address ({ip_str}) is not permitted",
                    )

                if ip.is_multicast:
                    return (
                        False,
                        f"Error: Multicast address ({ip_str}) is not permitted",
                    )

                if ip.is_unspecified:
                    return (
                        False,
                        f"Error: Unspecified address ({ip_str}) is not permitted",
                    )

                if ip.is_reserved:
                    return False, f"Error: Reserved address ({ip_str}) is not permitted"

                # Explicit check for cloud metadata endpoint
                if ip_str == "169.254.169.254":
                    return (
                        False,
                        "Error: Access to cloud metadata endpoint (169.254.169.254) is not permitted",
                    )

                # Additional IPv4 checks for specific dangerous ranges
                if isinstance(ip, ipaddress.IPv4Address):
                    # RFC1918 private ranges (redundant with is_private but explicit)
                    private_ranges = [
                        ipaddress.ip_network("10.0.0.0/8"),
                        ipaddress.ip_network("172.16.0.0/12"),
                        ipaddress.ip_network("192.168.0.0/16"),
                    ]
                    for private_range in private_ranges:
                        if ip in private_range:
                            return (
                                False,
                                f"Error: Private network address ({ip_str}) is not permitted",
                            )

                    # 127.0.0.0/8 localhost range
                    if ip in ipaddress.ip_network("127.0.0.0/8"):
                        return (
                            False,
                            f"Error: Localhost address ({ip_str}) is not permitted",
                        )

                    # 169.254.0.0/16 link-local range
                    if ip in ipaddress.ip_network("169.254.0.0/16"):
                        return (
                            False,
                            f"Error: Link-local address ({ip_str}) is not permitted",
                        )

                # IPv6 local addresses
                if isinstance(ip, ipaddress.IPv6Address):
                    if ip.is_site_local:
                        return (
                            False,
                            f"Error: Site-local IPv6 address ({ip_str}) is not permitted",
                        )

            except ValueError:
                return False, f"Error: Invalid IP address format: {ip_str}"

        # All checks passed
        return True, ""

    except Exception as e:
        return False, f"Error: URL validation failed: {str(e)}"


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

    # SSRF protection: validate URL before making any requests
    is_safe, error_msg = is_safe_url(url)
    if not is_safe:
        return error_msg

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
