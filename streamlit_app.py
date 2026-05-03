"""
Simple Weather Agent UI for Streamlit - Minimal version for testing
"""
import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Simple page config
st.set_page_config(
    page_title="Weather Agent",
    page_icon="🌤️",
    layout="wide"
)

# Title
st.title("🌤️ Weather Agent")
st.write("Get weather alerts and worldwide weather information")

# Simple API key input
groq_key = st.sidebar.text_input(
    "GROQ API Key",
    value=os.getenv("GROQ_API_KEY", ""),
    type="password",
    help="Get your free key at https://groq.com"
)

# Simple status check
if groq_key or os.getenv("GROQ_API_KEY"):
    st.success("✅ API Key configured")
else:
    st.warning("⚠️ Please provide your GROQ API key")

# Simple test button
if st.button("Test Connection"):
    st.write("Testing...")

    try:
        # Test imports
        from langchain_groq import ChatGroq
        from mcp_use import MCPAgent, MCPClient

        st.success("✅ All imports successful")

        # Test basic initialization
        config_file = "server/weather.json"
        if os.path.exists(config_file):
            st.success("✅ Config file found")
        else:
            st.error("❌ Config file not found")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.write("---")
st.write("**Example queries:**")
st.write("- Get weather alerts for CA")
st.write("- What's the weather in London?")
st.write("- Weather in Tokyo")
