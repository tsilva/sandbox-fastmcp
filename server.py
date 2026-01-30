from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

@mcp.tool
def letter_counter(text: str, letter: str) -> str:
    """Count how many times a letter appears in the given text."""
    return f"The letter '{letter}' appears {text.count(letter)} times in the text."

if __name__ == "__main__":
    mcp.run()
