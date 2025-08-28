import streamlit as st
import asyncio
import traceback
import ast  # To safely parse returned string to dictionary
from mcp import ClientSession
from mcp.client.sse import sse_client

def extract_result_structured_content(result_str):
    """
    Extract the 'result' value from the structuredContent dictionary string 
    (returned by MCP tool).
    """
    if "structuredContent=" in result_str:
        idx = result_str.find("structuredContent=")
        start = result_str.find("{", idx)
        end = result_str.find("}", start)
        if start != -1 and end != -1:
            dict_str = result_str[start:end+1]
            try:
                res_dict = ast.literal_eval(dict_str)
                return res_dict.get("result", result_str)
            except Exception:
                pass
    return result_str

async def call_tool(server_url: str, tool_name: str, arguments: dict) -> str:
    try:
        async with sse_client(server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                return str(result)
    except Exception as e:
        return f"Error: {e}\n{traceback.format_exc()}"

def main():
    st.title("Streamlit as an MCP Tool Host")
    st.write("Select a tool and provide inputs as required. The MCP server URL should be the SSE endpoint (e.g., http://localhost:8000/sse).")

    server_url = st.text_input("MCP Server SSE URL", "http://localhost:8000/sse")

    tool_name = st.selectbox(
        "Select Tool",
        [
            "summarize_dataset",
            "compute_mean",
            "compute_median",
            "compute_std",
            "get_stock_price"
        ]
    )

    arguments = {}
    if tool_name in ["compute_mean", "compute_median", "compute_std"]:
        arguments["column"] = st.text_input("Enter column name")
    elif tool_name == "get_stock_price":
        arguments["symbol"] = st.text_input("Enter stock symbol")

    if st.button("Run Tool"):
        st.info(f"Running '{tool_name}' tool on MCP server...")
        try:
            result = asyncio.run(call_tool(server_url, tool_name, arguments))
            relevant = extract_result_structured_content(result)
            st.subheader(f"{tool_name} Result")
            st.text_area("Result", str(relevant), height=80)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
