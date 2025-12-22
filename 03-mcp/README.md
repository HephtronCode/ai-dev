# FastMCP Demo Server 🚀

A Model Context Protocol (MCP) server implementation featuring arithmetic operations, web content extraction, and semantic documentation search capabilities.

## 📋 Overview

This project demonstrates a production-ready MCP server built with [FastMCP](https://github.com/jlowin/fastmcp) that exposes three powerful tools:

- **Arithmetic Operations**: Simple addition functionality for demonstration
- **Web Content Extraction**: Convert any webpage to clean Markdown using Jina Reader API
- **Semantic Documentation Search**: Search FastMCP documentation with TF-IDF based indexing

The server automatically downloads and indexes FastMCP documentation on startup, enabling intelligent search capabilities across markdown files.

## ✨ Features

- **Real-time Web Scraping**: Extract webpage content as Markdown with timeout handling
- **Semantic Search**: Fast TF-IDF based search with field boosting capabilities
- **Error Handling**: Comprehensive error handling for network requests and timeouts
- **Auto-indexing**: Automatic documentation download and indexing on server startup
- **Type Safety**: Full type hints for better code quality and IDE support

## 🔧 Prerequisites

- Python 3.13 or higher
- `uv` package manager (recommended) or `pip`

## 📦 Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd 03-mcp

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

### Using pip

```bash
# Clone the repository
git clone <your-repo-url>
cd 03-mcp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install fastmcp>=2.14.1 minsearch>=0.0.7 requests>=2.32.5
```

## 🚀 Usage

### Starting the MCP Server

```bash
# Run with uv
uv run main.py

# Or with standard Python
python main.py
```

On startup, the server will:

1. Download FastMCP documentation from GitHub
2. Extract and index all markdown files
3. Start the MCP server on the default port

### Available Tools

#### 1. **add** - Addition Tool

```python
# Add two integers
add(a=5, b=3)  # Returns: 8
```

#### 2. **get_page_content** - Web Content Extractor

```python
# Fetch webpage as Markdown
get_page_content(url="https://github.com/alexeygrigorev/minsearch", timeout=30)
# Returns: Markdown-formatted content
```

Features:

- URL validation
- Configurable timeout (default: 30s)
- Error handling for network issues
- Uses Jina Reader API for clean Markdown conversion

#### 3. **search_documentation** - Documentation Search

```python
# Search FastMCP docs
search_documentation(query="how to use context")
# Returns: List of relevant document snippets with sources
```

Features:

- TF-IDF based semantic search
- Field boosting for relevance
- Returns top 5 results with source filenames
- Truncated content (1500 chars) for context efficiency

## 📁 Project Structure

```
03-mcp/
├── main.py              # MCP server with all tools
├── solve_search.py      # Standalone search demo script
├── test_scrape.py       # Web scraping functionality tests
├── test_count.py        # Word count analysis demo
├── pyproject.toml       # Project configuration and dependencies
└── README.md            # This file
```

## 🧪 Testing

### Test Web Scraping

```bash
python test_scrape.py
```

Validates the `get_page_content` function by fetching content from a test URL.

### Test Word Count

```bash
python test_count.py
```

Demonstrates scraping a webpage and counting word occurrences.

### Test Documentation Search

```bash
uv run solve_search.py
```

Downloads FastMCP docs, indexes them, and performs a search query.

## 🛠️ Development

### Key Dependencies

- **fastmcp** (>=2.14.1): MCP server framework
- **minsearch** (>=0.0.7): Lightweight TF-IDF search engine
- **requests** (>=2.32.5): HTTP library for web requests

### How It Works

#### Web Content Extraction

1. Validates URL format (http/https)
2. Prepends Jina Reader API prefix (`https://r.jina.ai/`)
3. Fetches content with timeout protection
4. Returns Markdown-formatted text or error message

#### Documentation Search

1. **Initialization**: Downloads FastMCP repo ZIP from GitHub
2. **Extraction**: Unzips and filters markdown (.md/.mdx) files
3. **Indexing**: Builds TF-IDF index using minsearch
4. **Search**: Performs similarity search with field boosting
5. **Results**: Returns top 5 matches with source attribution

#### Search Index Configuration

- **Text Fields**: `["content"]` - Full text search
- **Keyword Fields**: `["filename"]` - Exact match filtering
- **Boost Dict**: `{"content": 1}` - Field weighting

## ⚠️ Known Issues & Solutions

### TypeError: 'FunctionTool' object is not callable

When importing functions decorated with `@mcp.tool`, they become `FunctionTool` objects. To make them callable in tests:

```python
# Instead of decorating
@mcp.tool
def my_function():
    pass

# Use registration
def my_function():
    pass
mcp.tool(my_function)  # Register as tool
```

### Missing timeout argument

Always include `timeout` in `requests.get()` calls to prevent indefinite hanging:

```python
response = requests.get(url, timeout=30)
```

## 📝 Configuration

The server uses these constants (configurable in [main.py](main.py)):

```python
DOCS_URL = "https://github.com/jlowin/fastmcp/archive/refs/heads/main.zip"
DEFAULT_TIMEOUT = 30  # seconds
NUM_SEARCH_RESULTS = 5
CONTENT_TRUNCATE_LENGTH = 1500  # characters
```

## 🤝 Contributing

This is a learning/demo project. Feel free to:

- Fork and experiment
- Report issues
- Suggest improvements
- Submit pull requests

## 📧 Contact

**Author**: Babatunde Abubakar  
**Email**: tunde.bouba@gmail.com

## 📄 License

MIT License - See project metadata for details.

## 🔗 Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Minsearch Library](https://github.com/alexeygrigorev/minsearch)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Jina Reader API](https://jina.ai/reader/)

## 🎯 Future Enhancements

- [ ] Add support for multiple documentation sources
- [ ] Implement caching for frequently accessed URLs
- [ ] Add more sophisticated search ranking algorithms
- [ ] Support for custom stop words in search
- [ ] Batch URL processing capabilities
- [ ] Integration with vector databases for semantic search
- [ ] CLI interface for standalone usage

---

**Built with ❤️ using FastMCP and Python**
