import pandas as pd
import httpx
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount
from mcp.server.sse import SseServerTransport

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("mcp_server")

# Load sample dataset
DATA_PATH = "data/sales_data.csv"
df = pd.read_csv(DATA_PATH)

# Tool 1: Get dataset summary
@mcp.tool()
def summarize_dataset() -> str:
    """Summarize the dataset: number of rows, columns, and columns names."""
    rows, cols = df.shape
    columns = ", ".join(df.columns)
    return f"Dataset has {rows} rows and {cols} columns. Columns: {columns}"

# Tool 2: Compute mean of a column
@mcp.tool()
def compute_mean(column: str) -> float:
    """Compute the mean of a numeric column."""
    if column not in df.columns:
        return f"Error: Column '{column}' not found."
    if not pd.api.types.is_numeric_dtype(df[column]):
        return f"Error: Column '{column}' is not numeric."
    return float(df[column].mean())

# Tool 3: Compute median of a column
@mcp.tool()
def compute_median(column: str) -> float:
    """Compute the median of a numeric column."""
    if column not in df.columns:
        return f"Error: Column '{column}' not found."
    if not pd.api.types.is_numeric_dtype(df[column]):
        return f"Error: Column '{column}' is not numeric."
    return float(df[column].median())

# Tool 4: Compute standard deviation of a column
@mcp.tool()
def compute_std(column: str) -> float:
    """Compute the standard deviation of a numeric column."""
    if column not in df.columns:
        return f"Error: Column '{column}' not found."
    if not pd.api.types.is_numeric_dtype(df[column]):
        return f"Error: Column '{column}' is not numeric."
    return float(df[column].std())

# Tool 5: Fetch stock price
@mcp.tool()
async def get_stock_price(symbol: str) -> str:
    """Fetch the latest stock price for a given ticker symbol."""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={api_key}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if "Time Series (5min)" not in data:
                return f"Error: No data found for symbol '{symbol}'."
            latest_time = list(data["Time Series (5min)"].keys())[0]
            price = data["Time Series (5min)"][latest_time]["4. close"]
            return f"Latest price for {symbol}: ${price}"
        except httpx.HTTPError:
            return f"Error: Failed to fetch stock price for '{symbol}'."

# Set up the SSE transport for MCP communication.
sse = SseServerTransport("/messages/")

async def handle_sse(request: Request) -> None:
    _server = mcp._mcp_server
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (reader, writer):
        await _server.run(reader, writer, _server.create_initialization_options())

# Create the Starlette app with two endpoints:
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Mount("/messages/", app=sse.handle_post_message),
    ],
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)