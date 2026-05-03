"""
Simple Weather Agent UI for Streamlit - Direct API version (no MCP)
"""
import streamlit as st
import asyncio
import os
import httpx
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

# Weather API functions (copied from server/weather.py)
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"
WTTR_API_BASE = "https://wttr.in"

async def make_nws_request(url: str):
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

async def make_weather_request(url: str):
    """Make a request to the wttr.in API with proper error handling."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc', 'Unknown')}
        Severity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', 'No description available')}
        Instructions: {props.get('instruction', 'No specific instructions provided')}
        """

def format_weather(data: dict) -> str:
    """Format weather data from wttr.in into a readable string."""
    if "error" in data:
        return f"Error fetching weather: {data['error']}"

    current = data.get("current_condition", [{}])[0]
    area = data.get("nearest_area", [{}])[0]

    location = f"{area.get('areaName', [{}])[0].get('value', 'Unknown')}, {area.get('country', [{}])[0].get('value', '')}"
    weather_desc = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
    temp = current.get("temp_C", "N/A")
    feels_like = current.get("FeelsLikeC", "N/A")
    humidity = current.get("humidity", "N/A")
    pressure = current.get("pressure", "N/A")
    wind_speed = current.get("windspeedKmph", "N/A")
    wind_dir = current.get("winddirDegree", "N/A")
    visibility = current.get("visibility", "N/A")

    return f"""
Location: {location}
Weather: {weather_desc}
Temperature: {temp}°C (Feels like: {feels_like}°C)
Humidity: {humidity}%
Pressure: {pressure} hPa
Wind: {wind_speed} km/h, Direction: {wind_dir}°
Visibility: {visibility} km
"""

async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state."""
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

async def get_weather(city: str) -> str:
    """Get current weather for a city worldwide."""
    url = f"{WTTR_API_BASE}/{city}?format=j1"
    data = await make_weather_request(url)

    if not data:
        return "Unable to fetch weather data."

    return format_weather(data)

# Test button
if st.button("Test Connection"):
    st.write("Testing...")

    try:
        # Test imports
        import httpx
        from langchain_groq import ChatGroq

        st.success("✅ All imports successful")

        # Test API connectivity
        async def test_weather():
            try:
                result = await get_weather("London")
                if "Error" not in result:
                    st.success("✅ Weather API working")
                else:
                    st.warning("⚠️ Weather API returned error")
            except Exception as e:
                st.error(f"❌ Weather API test failed: {e}")

        asyncio.run(test_weather())

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

    # Add user message
    st.session_state.messages.append({"role": "user", "content": text})

    # Process with AI + direct API calls
    with st.spinner("Thinking..."):
        try:
            # Simple keyword detection for now
            text_lower = text.lower()

            if "alert" in text_lower and any(state in text_lower for state in ["ca", "california", "ny", "new york", "tx", "texas", "fl", "florida"]):
                # Extract state code
                if "ca" in text_lower or "california" in text_lower:
                    state = "CA"
                elif "ny" in text_lower or "new york" in text_lower:
                    state = "NY"
                elif "tx" in text_lower or "texas" in text_lower:
                    state = "TX"
                elif "fl" in text_lower or "florida" in text_lower:
                    state = "FL"
                else:
                    state = "CA"  # default

                response = await get_alerts(state)
            elif any(word in text_lower for word in ["weather", "temperature", "forecast"]):
                # Extract city name (simple approach)
                words = text.split()
                city = "London"  # default
                for word in words:
                    if word[0].isupper():  # Likely a city name
                        city = word
                        break

                response = await get_weather(city)
            else:
                # Use AI for other queries
                from langchain_groq import ChatGroq

                llm = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    api_key=groq_key or os.getenv("GROQ_API_KEY")
                )

                # Simple prompt to help with weather queries
                prompt = f"""
                The user asked: "{text}"

                This is a weather assistant. Help them with weather-related queries.
                If they want weather alerts, suggest they ask for a specific US state.
                If they want weather, suggest they ask for a specific city.

                Keep your response helpful and concise.
                """

                response = llm.invoke(prompt).content

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
