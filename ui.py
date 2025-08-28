import streamlit as st
import httpx

st.title("MCP Server + Streamlit Demo (JSON-RPC)")

# Helper to call MCP JSON-RPC
def call_tool(method: str, params: dict = None):
    if params is None:
        params = {}
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": f"tools/{method}",
        "params": params,
    }
    try:
        resp = httpx.post("http://localhost:8000/mcp", json=payload)
        data = resp.json()
        if "result" in data:
            return data["result"]
        elif "error" in data:
            return f"Error: {data['error']}"
        else:
            return "Unexpected response format"
    except Exception as e:
        return f"Request failed: {e}"

    
# Dataset summary
if st.button("Show Dataset Summary"):
    st.write(call_tool("summarize_dataset"))

# Column statistics
column = st.text_input("Enter column name")
if st.button("Compute Mean"):
    st.write(call_tool("compute_mean", {"column": column}))

if st.button("Compute Median"):
    st.write(call_tool("compute_median", {"column": column}))

if st.button("Compute Standard Deviation"):
    st.write(call_tool("compute_std", {"column": column}))

# Stock price
symbol = st.text_input("Enter Stock Symbol")
if st.button("Get Stock Price"):
    st.write(call_tool("get_stock_price", {"symbol": symbol}))
