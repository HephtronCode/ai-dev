"""Test for web scraping functionality."""

from main import get_page_content


def test_get_page_content():
    """Test the get_page_content function."""
    url = "https://github.com/alexeygrigorev/minsearch"

    try:
        content = get_page_content(url)
        content_length = len(content)

        print(f"✓ Successfully fetched content from {url}")
        print(f"  Content length: {content_length} characters")

        # Basic validation
        if content_length > 0:
            print("✓ Content is not empty")
            return True
        print("✗ Content is empty")
        return False

    except (IOError, ValueError) as e:
        print(f"✗ Error fetching content: {e}")
        return False


if __name__ == "__main__":
    test_get_page_content()
