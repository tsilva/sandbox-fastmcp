<div align="center">
  <img src="logo.png" alt="sandbox-fastmcp" width="512"/>

  # sandbox-fastmcp

  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
  [![FastMCP](https://img.shields.io/badge/FastMCP-2.x-green.svg)](https://github.com/jlowin/fastmcp)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

  **A sandbox project for learning the [FastMCP](https://gofastmcp.com) framework.**
</div>

---

## Quick Start

### Install

```bash
pip install fastmcp
```

### Create a server

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def letter_counter(text: str, letter: str) -> str:
    """Count how many times a letter appears in the given text."""
    return f"The letter '{letter}' appears {text.count(letter)} times in the text."

if __name__ == "__main__":
    mcp.run()
```

### Run

```bash
python server.py
```

Or with the FastMCP CLI:

```bash
fastmcp run server.py:mcp
```

For HTTP transport:

```bash
fastmcp run server.py:mcp --transport http --port 8000
```

## License

MIT
