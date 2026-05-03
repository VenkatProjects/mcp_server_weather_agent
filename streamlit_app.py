"""
Simple Weather Agent UI for Streamlit - Working version
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

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.agent = None

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

# Initialize agent function
async def initialize_agent():
    if st.session_state.agent is None:
        try:
            from langchain_groq import ChatGroq
            from mcp_use import MCPAgent, MCPClient

            config_file = "server/weather.json"
            client = MCPClient.from_config_file(config_file)
            llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=groq_key or os.getenv("GROQ_API_KEY")
            )
            st.session_state.agent = MCPAgent(
                llm=llm,
                client=client,
                max_steps=15,
                memory_enabled=True,
            )
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize agent: {str(e)}")
            return False
    return True

# Test button
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
        st.error(f"❌ Import error: {str(e)}")

# Chat interface
st.subheader("💬 Chat")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("Ask about weather...")

async def process_message(text):
    if not groq_key and not os.getenv("GROQ_API_KEY"):
        st.error("Please provide your GROQ API key")
        return

    if not await initialize_agent():
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": text})

    # Add assistant response
    with st.spinner("Thinking..."):
        try:
            response = await st.session_state.agent.run(text)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

    st.rerun()

if user_input:
    asyncio.run(process_message(user_input))

# Examples
st.write("---")
st.write("**Example queries:**")
st.write("- Get weather alerts for CA")
st.write("- What's the weather in London?")
st.write("- Weather in Tokyo")
