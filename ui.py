import streamlit as st
import httpx

# -- MCP Server Connection Details --
API_URL = "http://127.0.0.1:6277"  # MCP proxy endpoint from terminal
SESSION_TOKEN = "edb625316bc20e0d75dbd5c65c5efce94db7f6d08951d99d7415cc8c3c1eeda1"
HEADERS = {"Authorization": f"Bearer {SESSION_TOKEN}"}

st.set_page_config(page_title="MCP Sales Dashboard", layout="centered")
st.title("Sales Data MCP Dashboard")

# 1. Show Dataset Summary Tool
if st.button("Show Dataset Summary"):
    try:
        resp = httpx.get(f"{API_URL}/summarize_dataset", headers=HEADERS)
        st.info(resp.text if resp.status_code == 200 else "Error: Could not get summary.")
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")

# 2. Column Statistics Input
st.subheader("Column Statistics")
column = st.text_input("Enter Column Name")

if column:
    col1, col2, col3 = st.columns(3)
    try:
        # Mean
        mean_resp = httpx.get(f"{API_URL}/compute_mean", params={"column": column}, headers=HEADERS)
        col1.metric("Mean", mean_resp.text if mean_resp.status_code == 200 else "Error")
        # Median
        med_resp = httpx.get(f"{API_URL}/compute_median", params={"column": column}, headers=HEADERS)
        col2.metric("Median", med_resp.text if med_resp.status_code == 200 else "Error")
        # Std Dev
        std_resp = httpx.get(f"{API_URL}/compute_std", params={"column": column}, headers=HEADERS)
        col3.metric("Std Dev", std_resp.text if std_resp.status_code == 200 else "Error")
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")

# 3. Stock Price Tool
st.subheader("Stock Price Checker")
symbol = st.text_input("Enter Stock Symbol (e.g. MSFT, AAPL)", "")
if st.button("Get Stock Price") and symbol:
    try:
        stock_resp = httpx.get(f"{API_URL}/get_stock_price", params={"symbol": symbol}, headers=HEADERS)
        st.success(stock_resp.text if stock_resp.status_code == 200 else "Error fetching price.")
    except Exception as e:
        st.error(f"Error: {e}")

st.caption("All analytics powered by MCP Tool Server via unified API.")
