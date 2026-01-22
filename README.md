<div align="center">
  <img src="logo.png" alt="sandbox-fastmcp" width="256"/>

  # sandbox-fastmcp

  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
  [![FastMCP](https://img.shields.io/badge/FastMCP-latest-green.svg)](https://github.com/jlowin/fastmcp)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
  [![W&B](https://img.shields.io/badge/Weights_&_Biases-integrated-yellow.svg)](https://wandb.ai)

  **🔬 Bridge your ML experiment tracking with AI assistants through the Model Context Protocol**

  [Features](#features) · [Quick Start](#quick-start) · [Usage](#usage) · [API Reference](#api-reference)
</div>

---

## Overview

sandbox-fastmcp demonstrates how to build MCP (Model Context Protocol) servers using the FastMCP framework. It includes a full-featured Weights & Biases integration that lets AI assistants query your ML experiments, visualize metrics, and compare runs—all through natural conversation.

## Features

- **List Projects & Runs** — Browse your wandb projects and filter runs by state
- **Retrieve Metrics** — Get detailed time-series data from any experiment run
- **Generate Visualizations** — Create line, scatter, and bar charts as base64 images
- **Compare Experiments** — Plot the same metric across multiple runs side-by-side
- **Connection Status** — Check wandb API health and user info via MCP resources

## Quick Start

### Installation

```bash
pip install -e .
```

### Prerequisites

Login to Weights & Biases:

```bash
wandb login
```

### Run the Server

```bash
python wandb_server.py
```

## Usage

### MCP Tools

| Tool | Description |
|------|-------------|
| `list_projects` | List wandb projects for an entity |
| `list_runs` | List runs with optional state filtering |
| `get_run_metrics` | Retrieve detailed metrics with time series data |
| `plot_metric_chart` | Create line/scatter/bar visualizations |
| `compare_runs_chart` | Compare a metric across multiple runs |

### MCP Resources

| Resource | Description |
|----------|-------------|
| `wandb://status` | Check API connection and user info |
| `wandb://help` | Usage documentation |

### Example: Listing Runs

```python
# Using the MCP client
from fastmcp import Client

async with Client("wandb_server.py") as client:
    runs = await client.call_tool("list_runs", {
        "entity": "my-team",
        "project": "my-project",
        "limit": 10,
        "state": "finished"
    })
```

### Example: Creating a Chart

```python
chart = await client.call_tool("plot_metric_chart", {
    "entity": "my-team",
    "project": "my-project",
    "run_id": "abc123",
    "metric_name": "train/loss",
    "chart_type": "line"
})
# Returns: data:image/png;base64,...
```

## API Reference

### list_projects

List wandb projects for a given entity.

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity` | str | Wandb entity (username or team name) |
| `limit` | int | Maximum projects to return (1-100, default: 10) |

### list_runs

List runs from a wandb project.

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity` | str | Wandb entity |
| `project` | str | Wandb project name |
| `limit` | int | Maximum runs to return (1-100, default: 10) |
| `state` | str | Filter: "running", "finished", "crashed", "failed" |

### get_run_metrics

Get detailed metrics and metadata for a specific run.

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity` | str | Wandb entity |
| `project` | str | Wandb project name |
| `run_id` | str | Run ID or name |

### plot_metric_chart

Create a chart for a specific metric.

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity` | str | Wandb entity |
| `project` | str | Wandb project name |
| `run_id` | str | Run ID or name |
| `metric_name` | str | Name of the metric to plot |
| `chart_type` | str | "line", "scatter", or "bar" (default: "line") |
| `title` | str | Custom chart title |
| `width` | int | Chart width in pixels (400-1200, default: 800) |
| `height` | int | Chart height in pixels (300-800, default: 600) |

### compare_runs_chart

Compare the same metric across multiple runs.

| Parameter | Type | Description |
|-----------|------|-------------|
| `entity` | str | Wandb entity |
| `project` | str | Wandb project name |
| `run_ids` | list | List of run IDs (2-10 runs) |
| `metric_name` | str | Name of the metric to compare |
| `chart_type` | str | "line" or "scatter" (default: "line") |
| `title` | str | Custom chart title |
| `width` | int | Chart width in pixels (400-1200, default: 800) |
| `height` | int | Chart height in pixels (300-800, default: 600) |

## Project Structure

```
sandbox-fastmcp/
├── server.py          # Basic MCP server example
├── wandb_server.py    # W&B integration server
├── client.py          # Example MCP client
└── pyproject.toml     # Project configuration
```

## Dependencies

- **fastmcp** — MCP server framework
- **wandb** — Weights & Biases SDK
- **matplotlib** — Chart generation
- **numpy** — Numerical operations
- **pandas** — Data manipulation

## License

MIT
