import fastmcp
from fastmcp import FastMCP

mcp = FastMCP("My MCP Server")

print(f"Server running on port: {fastmcp.settings.port}")
print(f"Server running on host: {fastmcp.settings.host}")

@mcp.tool
def letter_counter(text: str, letter:str) -> str:
    return f"The letter '{letter}' appears {text.count(letter)} times in the text."

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)