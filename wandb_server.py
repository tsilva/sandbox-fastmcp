#!/usr/bin/env python3
"""
Weights & Biases MCP Server

This server provides tools to connect to Weights & Biases (wandb) and plot charts
for metrics from runs. It's like having a data scientist's dashboard at your fingertips!

Think of this as a bridge between the powerful ML experiment tracking of wandb 
and the conversational interface of MCP - just like how a telescope brings distant 
stars closer to astronomers, this server brings your ML metrics closer to your AI assistant.
"""

import base64
import io
from typing import Dict, List, Optional, Union, Literal

import wandb
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from fastmcp import FastMCP, Context
from pydantic import Field
from typing import Annotated

# Initialize the FastMCP server
mcp = FastMCP(
    name="WandB-MCP-Server",
    instructions="""
    This server connects to Weights & Biases (wandb) to retrieve and visualize 
    ML experiment data. Use it to:
    - List projects and runs
    - Get run metrics and metadata
    - Plot charts for specific metrics
    - Compare metrics across multiple runs
    
    Make sure you have wandb API key configured before using these tools.
    """
)

class WandbConnection:
    """Manages wandb API connection and caching."""
    
    def __init__(self):
        self.api = None
        self._projects_cache = {}
        self._runs_cache = {}
    
    def get_api(self):
        """Initialize wandb API if not already done."""
        if self.api is None:
            try:
                self.api = wandb.Api()
            except Exception as e:
                raise ConnectionError(f"Failed to initialize wandb API. Make sure you're logged in: {e}")
        return self.api
    
    def get_project(self, entity: str, project: str):
        """Get a project with caching."""
        key = f"{entity}/{project}"
        if key not in self._projects_cache:
            api = self.get_api()
            try:
                self._projects_cache[key] = api.project(name=project, entity=entity)
            except Exception as e:
                raise ValueError(f"Project '{project}' not found for entity '{entity}': {e}")
        return self._projects_cache[key]

# Global connection instance
wandb_conn = WandbConnection()

@mcp.tool()
async def list_projects(
    entity: Annotated[str, Field(description="Wandb entity (username or team name)")],
    limit: Annotated[int, Field(description="Maximum number of projects to return", ge=1, le=100)] = 10,
    ctx: Optional[Context] = None
) -> List[Dict[str, str]]:
    """
    List wandb projects for a given entity.
    
    Like browsing through a library's catalog, this shows you all the available
    projects (experiment collections) for a specific user or team.
    """
    if ctx:
        await ctx.info(f"Fetching projects for entity: {entity}")
    
    try:
        api = wandb_conn.get_api()
        projects = api.projects(entity=entity)
        
        result = []
        for i, project in enumerate(projects):
            if i >= limit:
                break
            result.append({
                "name": project.name,
                "entity": project.entity,
                "description": getattr(project, 'description', '') or '',
                "created_at": str(getattr(project, 'created_at', '')),
                "url": f"https://wandb.ai/{entity}/{project.name}"
            })
        
        if ctx:
            await ctx.info(f"Found {len(result)} projects")
        
        return result
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching projects: {e}")
        raise RuntimeError(f"Failed to fetch projects: {e}")

@mcp.tool()
async def list_runs(
    entity: Annotated[str, Field(description="Wandb entity (username or team name)")],
    project: Annotated[str, Field(description="Wandb project name")],
    limit: Annotated[int, Field(description="Maximum number of runs to return", ge=1, le=100)] = 10,
    state: Annotated[Optional[Literal["running", "finished", "crashed", "failed"]], Field(description="Filter by run state")] = None,
    ctx: Optional[Context] = None
) -> List[Dict[str, Union[str, Dict]]]:
    """
    List runs from a wandb project.
    
    Think of this as getting a table of contents for all experiments in a project -
    each run represents one experimental attempt with its own story to tell.
    """
    if ctx:
        await ctx.info(f"Fetching runs for {entity}/{project}")
    
    try:
        api = wandb_conn.get_api()
        
        # Build filters
        filters = {}
        if state:
            filters["state"] = state
            
        runs = api.runs(path=f"{entity}/{project}", filters=filters)
        
        result = []
        for i, run in enumerate(runs):
            if i >= limit:
                break
                
            result.append({
                "id": run.id,
                "name": run.name or run.id,
                "state": run.state,
                "created_at": str(run.created_at) if run.created_at else '',
                "runtime": str(run.summary.get('_runtime', 0)) + ' seconds' if run.summary else '',
                "config": dict(run.config) if run.config else {},
                "summary": dict(run.summary) if run.summary else {},
                "url": run.url,
                "tags": list(run.tags) if run.tags else []
            })
        
        if ctx:
            await ctx.info(f"Found {len(result)} runs")
        
        return result
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching runs: {e}")
        raise RuntimeError(f"Failed to fetch runs: {e}")

@mcp.tool()
async def get_run_metrics(
    entity: Annotated[str, Field(description="Wandb entity (username or team name)")],
    project: Annotated[str, Field(description="Wandb project name")],
    run_id: Annotated[str, Field(description="Run ID or name")],
    ctx: Optional[Context] = None
) -> Dict[str, Union[str, Dict, List]]:
    """
    Get detailed metrics and metadata for a specific run.
    
    Like opening a scientist's lab notebook, this gives you all the detailed
    measurements and observations from a particular experiment.
    """
    if ctx:
        await ctx.info(f"Fetching metrics for run {run_id}")
    
    try:
        api = wandb_conn.get_api()
        run = api.run(f"{entity}/{project}/{run_id}")
        
        # Get history (time series data)
        history = run.history()
        
        # Convert history to a more readable format
        metrics_over_time = {}
        if not history.empty:
            for column in history.columns:
                if column not in ['_step', '_runtime', '_timestamp']:
                    metrics_over_time[column] = {
                        'values': history[column].dropna().tolist(),
                        'steps': history.loc[history[column].notna(), '_step'].tolist() if '_step' in history.columns else list(range(len(history[column].dropna()))),
                        'final_value': history[column].iloc[-1] if not history[column].dropna().empty else None
                    }
        
        result = {
            "id": run.id,
            "name": run.name or run.id,
            "state": run.state,
            "created_at": str(run.created_at) if run.created_at else '',
            "config": dict(run.config) if run.config else {},
            "summary": dict(run.summary) if run.summary else {},
            "tags": list(run.tags) if run.tags else [],
            "url": run.url,
            "metrics_over_time": metrics_over_time,
            "available_metrics": list(metrics_over_time.keys())
        }
        
        if ctx:
            await ctx.info(f"Retrieved {len(metrics_over_time)} metrics for run {run_id}")
        
        return result
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Error fetching run metrics: {e}")
        raise RuntimeError(f"Failed to fetch run metrics: {e}")

@mcp.tool()
async def plot_metric_chart(
    entity: Annotated[str, Field(description="Wandb entity (username or team name)")],
    project: Annotated[str, Field(description="Wandb project name")],
    run_id: Annotated[str, Field(description="Run ID or name")],
    metric_name: Annotated[str, Field(description="Name of the metric to plot")],
    chart_type: Annotated[Literal["line", "scatter", "bar"], Field(description="Type of chart to create")] = "line",
    title: Annotated[Optional[str], Field(description="Custom title for the chart")] = None,
    width: Annotated[int, Field(description="Chart width in pixels", ge=400, le=1200)] = 800,
    height: Annotated[int, Field(description="Chart height in pixels", ge=300, le=800)] = 600,
    ctx: Optional[Context] = None
) -> str:
    """
    Create a chart for a specific metric from a wandb run.
    
    Like a telescope that transforms distant light into visible images, this tool
    transforms your numerical metrics into visual insights that tell the story
    of your model's learning journey.
    """
    if ctx:
        await ctx.info(f"Creating {chart_type} chart for metric '{metric_name}' from run {run_id}")
    
    try:
        # Get run data
        api = wandb_conn.get_api()
        run = api.run(f"{entity}/{project}/{run_id}")
        history = run.history()
        
        if history.empty:
            raise ValueError(f"No history data found for run {run_id}")
        
        if metric_name not in history.columns:
            available_metrics = [col for col in history.columns if not col.startswith('_')]
            raise ValueError(f"Metric '{metric_name}' not found. Available metrics: {available_metrics}")
        
        # Prepare data
        metric_data = history[metric_name].dropna()
        if metric_data.empty:
            raise ValueError(f"No data points found for metric '{metric_name}'")
        
        steps = history.loc[metric_data.index, '_step'] if '_step' in history.columns else range(len(metric_data))
        
        # Create the plot
        plt.figure(figsize=(width/100, height/100))
        
        if chart_type == "line":
            plt.plot(steps, metric_data, linewidth=2, marker='o', markersize=4)
        elif chart_type == "scatter":
            plt.scatter(steps, metric_data, alpha=0.7)
        elif chart_type == "bar":
            plt.bar(steps, metric_data, alpha=0.7)
        
        # Customize the plot
        chart_title = title or f"{metric_name} - {run.name or run_id}"
        plt.title(chart_title, fontsize=14, fontweight='bold')
        plt.xlabel('Step', fontsize=12)
        plt.ylabel(metric_name, fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add some styling
        plt.tight_layout()
        
        # Convert to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        if ctx:
            await ctx.info(f"Chart created successfully with {len(metric_data)} data points")
        
        # Return as data URL for easy display
        return f"data:image/png;base64,{chart_base64}"
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Error creating chart: {e}")
        raise RuntimeError(f"Failed to create chart: {e}")

@mcp.tool()
async def compare_runs_chart(
    entity: Annotated[str, Field(description="Wandb entity (username or team name)")],
    project: Annotated[str, Field(description="Wandb project name")],
    run_ids: Annotated[List[str], Field(description="List of run IDs or names to compare", min_length=2, max_length=10)],
    metric_name: Annotated[str, Field(description="Name of the metric to compare")],
    chart_type: Annotated[Literal["line", "scatter"], Field(description="Type of chart to create")] = "line",
    title: Annotated[Optional[str], Field(description="Custom title for the chart")] = None,
    width: Annotated[int, Field(description="Chart width in pixels", ge=400, le=1200)] = 800,
    height: Annotated[int, Field(description="Chart height in pixels", ge=300, le=800)] = 600,
    ctx: Optional[Context] = None
) -> str:
    """
    Create a comparison chart showing the same metric across multiple runs.
    
    Like comparing the growth patterns of different plants under various conditions,
    this tool lets you see how the same metric evolves across different experimental runs.
    """
    if ctx:
        await ctx.info(f"Creating comparison chart for {len(run_ids)} runs")
    
    try:
        api = wandb_conn.get_api()
        
        plt.figure(figsize=(width/100, height/100))
        colors = plt.cm.tab10(np.linspace(0, 1, len(run_ids)))
        
        for i, run_id in enumerate(run_ids):
            if ctx:
                await ctx.info(f"Processing run {i+1}/{len(run_ids)}: {run_id}")
            
            try:
                run = api.run(f"{entity}/{project}/{run_id}")
                history = run.history()
                
                if history.empty or metric_name not in history.columns:
                    if ctx:
                        await ctx.warning(f"Metric '{metric_name}' not found in run {run_id}")
                    continue
                
                metric_data = history[metric_name].dropna()
                if metric_data.empty:
                    if ctx:
                        await ctx.warning(f"No data points for metric '{metric_name}' in run {run_id}")
                    continue
                
                steps = history.loc[metric_data.index, '_step'] if '_step' in history.columns else range(len(metric_data))
                
                label = run.name if run.name and run.name != run_id else run_id
                
                if chart_type == "line":
                    plt.plot(steps, metric_data, label=label, color=colors[i], linewidth=2, marker='o', markersize=3)
                elif chart_type == "scatter":
                    plt.scatter(steps, metric_data, label=label, color=colors[i], alpha=0.7)
                    
            except Exception as e:
                if ctx:
                    await ctx.warning(f"Error processing run {run_id}: {e}")
                continue
        
        # Customize the plot
        chart_title = title or f"{metric_name} Comparison"
        plt.title(chart_title, fontsize=14, fontweight='bold')
        plt.xlabel('Step', fontsize=12)
        plt.ylabel(metric_name, fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Convert to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        chart_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        if ctx:
            await ctx.info("Comparison chart created successfully")
        
        return f"data:image/png;base64,{chart_base64}"
        
    except Exception as e:
        if ctx:
            await ctx.error(f"Error creating comparison chart: {e}")
        raise RuntimeError(f"Failed to create comparison chart: {e}")

@mcp.resource("wandb://status")
async def wandb_status(ctx: Optional[Context] = None) -> Dict[str, Union[str, bool]]:
    """
    Check wandb connection status and configuration.
    
    Like checking if your telescope is properly calibrated before stargazing,
    this tells you if wandb is ready to use.
    """
    try:
        api = wandb_conn.get_api()
        
        # Try to get user info to verify connection
        try:
            user_info = api.user()
            username = getattr(user_info, 'username', 'unknown')
            teams = getattr(user_info, 'teams', [])
            team_names = [team.get('name', 'unknown') if isinstance(team, dict) else str(team) for team in teams] if teams else []
        except:
            username = 'unknown'
            team_names = []
        
        return {
            "status": "connected",
            "api_available": True,
            "username": username,
            "teams": team_names,
            "wandb_version": wandb.__version__,
            "message": "Wandb API is ready to use"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "api_available": False,
            "username": "",
            "teams": [],
            "wandb_version": wandb.__version__,
            "message": f"Wandb connection failed: {e}"
        }

@mcp.resource("wandb://help")
async def wandb_help() -> str:
    """
    Get help and usage examples for the wandb MCP server.
    
    Your friendly guide to navigating the wandb MCP server capabilities.
    """
    return """
# Weights & Biases MCP Server Help

## Overview
This server connects to Weights & Biases (wandb) to retrieve and visualize ML experiment data.

## Prerequisites
1. Install wandb: `pip install wandb`
2. Login to wandb: `wandb login`
3. Have access to wandb projects you want to analyze

## Available Tools

### 1. list_projects
List all projects for a specific entity (user or team).
Example: List projects for user "john_doe"

### 2. list_runs  
List runs from a specific project with optional filtering.
Example: List last 20 finished runs from "my-ml-project"

### 3. get_run_metrics
Get detailed metrics and metadata for a specific run.
Example: Get all metrics for run "amazing-run-123"

### 4. plot_metric_chart
Create a chart for a specific metric from a run.
Example: Plot training loss over time as a line chart

### 5. compare_runs_chart
Compare the same metric across multiple runs.
Example: Compare validation accuracy across 3 different experiments

## Available Resources

- wandb://status - Check connection status
- wandb://help - This help document

## Usage Tips

1. Always start by checking wandb://status to ensure connection
2. Use list_projects and list_runs to explore available data
3. Use get_run_metrics to see what metrics are available for plotting
4. Create visualizations with plot_metric_chart for single runs
5. Use compare_runs_chart to compare multiple experiments

## Error Handling

The server provides detailed error messages if:
- Wandb is not properly configured
- Projects or runs don't exist  
- Metrics are not available
- Connection issues occur

Make sure you're logged into wandb and have access to the requested projects.
"""

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()