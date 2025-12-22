"""Module for searching documents using minsearch indexing."""

import io
import zipfile

import requests

import minsearch

# Constants
URL = "https://github.com/jlowin/fastmcp/archive/refs/heads/main.zip"


def download_and_index_documents():
    """Download documentation and build the search index.

    Returns:
        tuple: (index, documents) - The fitted search index and list of documents
    """
    # 1. Download the repository
    print(f"Downloading {URL}...")
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to download: {e}")
        raise

    # 2. Extract and Process Files
    documents = []

    # Use io.BytesIO to read the downloaded bytes as a zip file in memory
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for file_info in z.infolist():
            # Only process .md and .mdx files
            if file_info.filename.endswith(".md") or file_info.filename.endswith(
                ".mdx"
            ):
                # Logic: Remove the first part of the path
                # e.g., "fastmcp-main/docs/welcome.md" -> "docs/welcome.md"
                if "/" in file_info.filename:
                    clean_filename = file_info.filename.split("/", 1)[1]
                else:
                    clean_filename = file_info.filename

                # Skip empty filenames or directories
                if not clean_filename:
                    continue

                # Read content
                text = z.read(file_info).decode("utf-8")

                # Add to list
                documents.append({"filename": clean_filename, "content": text})

    print(f"Indexed {len(documents)} documents.")

    # 3. Create Minsearch Index
    index = minsearch.Index(
        text_fields=["content"],  # Fields to search text within
        keyword_fields=[
            "filename"
        ],  # Fields to filter by exact match (standard practice)
    )

    index.fit(documents)

    return index, documents


def search(index, search_query):
    """Search the index for documents matching the query.

    Args:
        index: The minsearch Index instance
        search_query: The search query string.

    Returns:
        List of matching documents.
    """
    search_results = index.search(
        query=search_query,
        boost_dict={"content": 1},
        num_results=5,  # simple boost config
    )
    return search_results


def main():
    """Main function to demonstrate search functionality."""
    # Download and index documents
    index, documents = download_and_index_documents()

    # 5. TEST IT (The Homework Question)
    QUERY = "demo"
    results = search(index, QUERY)

    print("\n--- Search Results for 'demo' ---")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['filename']}")

    print("\nANSWER FOR HOMEWORK:")
    if results:
        print(f"The first file returned is: {results[0]['filename']}")


if __name__ == "__main__":
    main()
