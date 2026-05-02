"""
FastMCP weather example with US alerts and global weather.

Run from the repository root:
    uv run server/weather.py
"""
from typing import Any
import os
import httpx

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("weather")

# NWS API for US alerts
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# OpenWeatherMap API for global weather (optional, but wttr.in is used instead for no-key)
# OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5/weather"
# API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Optional now

# wttr.in API for global weather (free, no key needed)
WTTR_API_BASE = "https://wttr.in"


async def make_nws_request(url: str) -> dict[str, Any] | None:
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


async def make_weather_request(url: str) -> dict[str, Any] | None:
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
    feels_like = current.get("FeelsLikeC", "N/A")  # wttr.in has FeelsLikeC
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


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_weather(city: str) -> str:
    """Get current weather for a city worldwide.

    Args:
        city: City name (e.g., London, New York, Tokyo, Bangalore)
    """
    url = f"{WTTR_API_BASE}/{city}?format=j1"
    data = await make_weather_request(url)

    if not data:
        return "Unable to fetch weather data."

    return format_weather(data)


@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"


def run_server():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    run_server()