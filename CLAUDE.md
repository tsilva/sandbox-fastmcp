# CLAUDE.md

## Project Overview

Sandbox project for learning the FastMCP (Model Context Protocol) framework. Contains a simple MCP server example in `server.py`.

## Core Pattern

```python
from fastmcp import FastMCP

mcp = FastMCP("Server Name")

@mcp.tool
def my_tool(param: str) -> str:
    """Tool description."""
    return result

if __name__ == "__main__":
    mcp.run()
```

## Running

```bash
python server.py           # stdio transport (default)
fastmcp run server.py:mcp  # via CLI
fastmcp run server.py:mcp --transport http --port 8000  # HTTP
```

## Dependencies

Install: `pip install fastmcp`

## Project Standards

### README.md Maintenance
Keep README.md up to date with any significant project changes.
