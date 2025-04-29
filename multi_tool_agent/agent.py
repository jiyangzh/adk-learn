import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import os
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


def get_weather(city: str) -> Dict[str, str]:
    """Retrieves the current weather report for a specified city using WeatherAPI.com.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        return {"status": "error", "error_message": "WeatherAPI key not configured"}

    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,
        "aqi": "no",  # We don't need air quality data for basic weather
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]

        return {
            "status": "success",
            "condition": condition.lower(),
            "temperature_c": f"{temp_c:.1f}",
            "temperature_f": f"{temp_f:.1f}",
            "city_name": city,
            # "report": (
            #     f"The weather in {city} is {condition.lower()} with a temperature of "
            #     f"{temp_c:.1f} degrees Celsius ({temp_f:.1f} degrees Fahrenheit)."
            # ),
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available: {str(e)}",
        }


def get_forcast(city: str, days: int = 7) -> Dict[str, str]:
    """Retrieves the forecast weather report for a specified city using WeatherAPI.com.

    Args:
        city (str): The name of the city for which to retrieve the weather report.
        days (int): How many days forecast for weather

    Returns:
        dict: status and result or error msg.
    """
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        return {"status": "error", "error_message": "WeatherAPI key not configured"}

    base_url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": api_key,
        "q": city,
        "days": days,
        "aqi": "no",  # We don't need air quality data for basic weather
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        return data
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available: {str(e)}",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (f"Sorry, I don't have timezone information for {city}."),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = f"The current time in {city} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"
    return {"status": "success", "report": report}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash-exp",
    description=("Agent to answer questions about the time and weather in a city."),
    instruction=("I can answer your questions about the time and weather in a city."),
    tools=[get_weather, get_current_time, get_forcast],
)
