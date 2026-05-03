"""
Modern & Professional Weather Agent UI using Streamlit
Enhanced with custom CSS, advanced components, and professional design
"""
import streamlit as st
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient

# Load environment variables
load_dotenv()

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Weather Agent Pro",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Weather Agent Pro\nPowered by AI and Real-time Weather APIs"
    }
)

# ==================== CUSTOM CSS & STYLING ====================
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    header {
        background: transparent !important;
        border-bottom: none !important;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        display: flex;
        gap: 0.5rem;
    }
    
    .chat-message.user {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .chat-message.assistant {
        background-color: #f3e5f5;
        border-left: 4px solid #764ba2;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border-radius: 0.5rem;
        border: none;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stChatInputContainer > div > div > input {
        border-radius: 0.5rem;
        border: 2px solid #ddd;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stChatInputContainer > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Cards styling */
    .card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid #f0f0f0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    .status-active {
        background-color: #c8e6c9;
        color: #1b5e20;
    }
    
    .status-inactive {
        background-color: #ffccbc;
        color: #bf360c;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-bottom: 3px solid transparent;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        border-bottom-color: #667eea !important;
        color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== INITIALIZATION ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.agent = None
    st.session_state.api_configured = False

# ==================== SIDEBAR - CONFIGURATION ====================
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.divider()
    
    # API Key input with better UX
    groq_key = st.text_input(
        "🔑 GROQ API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        help="Get your free API key at https://groq.com",
        placeholder="Enter your GROQ API key"
    )
    
    # Status indicator
    if groq_key or os.getenv("GROQ_API_KEY"):
        st.markdown('<span class="status-badge status-active">✓ API Configured</span>', unsafe_allow_html=True)
        st.session_state.api_configured = True
    else:
        st.markdown('<span class="status-badge status-inactive">✗ API Not Configured</span>', unsafe_allow_html=True)
        st.session_state.api_configured = False
    
    st.markdown("---")
    
    # Helper text
    st.markdown("""
    ### 📚 Getting Started
    
    1. **Get API Key**: Visit [groq.com](https://groq.com)
    2. **Set Key**: Paste your API key above
    3. **Start Chat**: Ask about weather!
    """)
    
    st.markdown("---")
    
    # Control buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.agent = None
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent = None
            st.rerun()

# ==================== INITIALIZE AGENT ====================
async def initialize_agent():
    """Initialize MCP Agent with error handling"""
    if st.session_state.agent is None:
        try:
            with st.spinner("🚀 Initializing Weather Agent..."):
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

# ==================== MAIN CONTENT ====================

# Header section
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("# 🌦️ Weather Agent Pro")
    st.markdown("*Intelligent weather information powered by AI*")
with col2:
    st.markdown(f"<div style='text-align: right; margin-top: 1rem;'><small>Last updated: {datetime.now().strftime('%H:%M:%S')}</small></div>", unsafe_allow_html=True)

st.divider()

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📋 Features", "❓ Help"])

# ==================== TAB 1: CHAT ====================
with tab1:
    if not st.session_state.api_configured and not os.getenv("GROQ_API_KEY"):
        st.warning(
            "🔑 **API Key Required**\n\n"
            "Please configure your GROQ API key in the sidebar to start using the Weather Agent."
        )
    else:
        # Chat container
        st.markdown("### 💬 Conversation")
        
        # Display chat messages with styling
        chat_container = st.container()
        with chat_container:
            if len(st.session_state.messages) == 0:
                st.info("""
                👋 **Welcome to Weather Agent Pro!**
                
                Try asking:
                - "Get weather alerts for CA"
                - "What's the weather in London?"
                - "Show me weather for Tokyo"
                """)
            else:
                for i, message in enumerate(st.session_state.messages):
                    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
                        st.markdown(message["content"])
        
        # Chat input
        st.markdown("---")
        user_input = st.chat_input(
            "Ask about weather alerts or weather conditions... (e.g., 'Weather in London' or 'Alerts for CA')"
        )
        
        # Process message
        async def process_message(user_text):
            if not st.session_state.api_configured and not os.getenv("GROQ_API_KEY"):
                st.error("Please provide your GROQ API key in the sidebar")
                return
            
            if not await initialize_agent():
                return
            
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_text})
            
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_text)
            
            # Get agent response
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("🔍 Analyzing weather data..."):
                    try:
                        response = await st.session_state.agent.run(user_text)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.markdown(response)
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        if user_input:
            asyncio.run(process_message(user_input))

# ==================== TAB 2: FEATURES ====================
with tab2:
    st.markdown("### ✨ Available Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🚨 US Weather Alerts
        - **Coverage**: All US states
        - **Source**: National Weather Service (NWS)
        - **Updates**: Real-time
        - **Cost**: Free, no API key needed
        
        **Example Query:**
        > "Get weather alerts for California"
        """)
    
    with col2:
        st.markdown("""
        #### 🌍 Global Weather
        - **Coverage**: Worldwide
        - **Data**: Current conditions
        - **Temperature**: Celsius/Fahrenheit
        - **Includes**: Humidity, pressure, wind
        
        **Example Query:**
        > "What's the weather in London?"
        """)
    
    st.divider()
    
    st.markdown("### 🔧 Technical Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Model", "Groq LLaMA", "Latest")
    with col2:
        st.metric("Weather API", "wttr.in", "Free")
    with col3:
        st.metric("Alerts API", "NWS", "Free")

# ==================== TAB 3: HELP ====================
with tab3:
    st.markdown("### ❓ Frequently Asked Questions")
    
    with st.expander("🔑 How do I get a GROQ API key?"):
        st.markdown("""
        1. Visit [https://groq.com](https://groq.com)
        2. Sign up for a free account
        3. Go to API console
        4. Create an API key
        5. Copy and paste it in the Configuration sidebar
        """)
    
    with st.expander("🌍 What weather data sources are used?"):
        st.markdown("""
        - **US Alerts**: National Weather Service (NWS) API - Free
        - **Global Weather**: wttr.in API - Free (no key required)
        - **AI Processing**: Groq LLaMA 3.3 70B
        """)
    
    with st.expander("⚡ What queries can I make?"):
        st.markdown("""
        **Alert Queries:**
        - "Get weather alerts for CA"
        - "What are the active alerts in Texas?"
        - "Show me severe weather alerts"
        
        **Weather Queries:**
        - "What's the weather in London?"
        - "Weather in Tokyo"
        - "Tell me the conditions in New York"
        - "Is it raining in Mumbai?"
        """)
    
    with st.expander("🚀 How is this deployed?"):
        st.markdown("""
        Currently running on **Streamlit Cloud** - a modern Python app hosting platform
        that makes deployment easy and free for public applications.
        """)
    
    with st.expander("💾 Is my conversation saved?"):
        st.markdown("""
        Yes! The Weather Agent has built-in conversation memory enabled.
        Your chat history is maintained during your session for context-aware responses.
        """)

# ==================== FOOTER ====================
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.85rem; margin-top: 2rem;'>
    <p>🌦️ Weather Agent Pro | Powered by Streamlit + Groq LLaMA</p>
    <p><small>Real-time weather data from NWS and wttr.in</small></p>
</div>
""", unsafe_allow_html=True)
