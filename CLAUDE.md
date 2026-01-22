# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a sandbox project demonstrating the FastMCP (Model Context Protocol) framework. It includes three MCP server implementations:
- `server.py`: Basic example with a letter counter tool
- `wandb_server.py`: Full-featured Weights & Biases integration with visualization capabilities
- `client.py`: Example MCP client implementation

## Core Architecture

### FastMCP Framework
The project uses the `fastmcp` library to build MCP servers. Key patterns:

1. **Server initialization**: `mcp = FastMCP(name="Server Name", instructions="...")`
2. **Tool registration**: Use `@mcp.tool()` decorator for exposing functions as tools
3. **Resource registration**: Use `@mcp.resource()` decorator for providing queryable resources
4. **Context object**: Optional `Context` parameter provides logging (`ctx.info()`, `ctx.error()`, `ctx.warning()`)
5. **Type annotations**: Use Pydantic's `Annotated` with `Field` for parameter documentation

### wandb_server.py Architecture

This is the primary server implementation with the following design:

- **Connection Management**: `WandbConnection` class manages the wandb API singleton and caching
  - Caches projects and runs to reduce API calls
  - Lazy initialization of wandb API
  - Located at wandb_server.py:40-69

- **Tools** (5 main functions):
  1. `list_projects()`: List wandb projects for an entity
  2. `list_runs()`: List runs with optional state filtering
  3. `get_run_metrics()`: Retrieve detailed metrics with time series data
  4. `plot_metric_chart()`: Create matplotlib visualizations (line/scatter/bar)
  5. `compare_runs_chart()`: Multi-run metric comparison

- **Resources** (2 endpoints):
  1. `wandb://status`: Check API connection and user info
  2. `wandb://help`: Usage documentation

- **Visualization Pattern**: Charts are generated as base64-encoded PNG data URLs using matplotlib
  - Creates plots in memory with `io.BytesIO()`
  - Returns format: `data:image/png;base64,{encoded_data}`

## Development Commands

### Running the Servers

**Basic server** (port 9000):
```bash
python server.py
```

**Wandb server** (default FastMCP settings):
```bash
python wandb_server.py
```

**Client example**:
```bash
python client.py
```

### Dependencies

Install all dependencies:
```bash
pip install -e .
```

Core dependencies: fastmcp, wandb, matplotlib, numpy, pandas, scikit-learn

### Wandb Setup

Before using `wandb_server.py`:
```bash
wandb login
```

Ensure you have access to the wandb projects you want to query.

## Important Implementation Notes

### Type Annotations
Always use `Annotated[type, Field(description="...", ...)]` for tool parameters to provide proper documentation in the MCP protocol. Example:
```python
@mcp.tool()
async def my_tool(
    param: Annotated[str, Field(description="Description here")],
    ctx: Optional[Context] = None
) -> ReturnType:
```

### Error Handling
- Use try-except blocks in all tools
- Log errors via `ctx.error()` before raising
- Provide helpful error messages indicating what went wrong and how to fix it

### Context Logging
Use the Context object for observability:
- `ctx.info()`: Progress updates
- `ctx.warning()`: Non-fatal issues
- `ctx.error()`: Errors before raising exceptions

### Async Functions
All MCP tools and resources should be async functions (use `async def`).

### Chart Generation
When creating new visualization tools:
- Use `plt.figure(figsize=(width/100, height/100))` for size control
- Always call `plt.close()` after saving to buffer
- Return base64 data URLs for easy embedding

## Project Standards

### README.md Maintenance
Keep README.md up to date with any significant project changes, including:
- New MCP tools or resources
- Changes to setup/installation steps
- Updates to API requirements or authentication
- New example usage patterns
