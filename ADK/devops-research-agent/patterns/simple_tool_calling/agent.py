import os
from datetime import datetime
from zoneinfo import ZoneInfo

from google.adk import Agent


CITY_TIMEZONES = {
    "austin": "America/Chicago",
    "chicago": "America/Chicago",
    "denver": "America/Denver",
    "london": "Europe/London",
    "los angeles": "America/Los_Angeles",
    "new york": "America/New_York",
    "san francisco": "America/Los_Angeles",
    "seattle": "America/Los_Angeles",
    "tokyo": "Asia/Tokyo",
}


def get_current_time(city: str) -> dict:
    """Return the current local time for a supported city.

    Args:
        city: City name, such as Austin, Denver, seattle , Los_Angeles, New York, London, or Tokyo.
    """
    normalized_city = city.strip().lower()
    timezone_name = CITY_TIMEZONES.get(normalized_city)

    if timezone_name is None:
        supported = ", ".join(sorted(CITY_TIMEZONES))
        return {
            "status": "error",
            "error_message": (
                f"I do not have timezone data for {city!r}. "
                f"Try one of: {supported}."
            ),
        }

    now = datetime.now(ZoneInfo(timezone_name))
    return {
        "status": "success",
        "city": city,
        "timezone": timezone_name,
        "time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
    }


def calculate(operation: str, left: float, right: float) -> dict:
    """Add or multiply two numbers.

    Args:
        operation: Use "add" for addition or "multiply" for multiplication.
        left: The first number.
        right: The second number.
    """
    normalized_operation = operation.strip().lower()

    if normalized_operation == "add":
        result = left + right
    elif normalized_operation == "multiply":
        result = left * right
    else:
        return {
            "status": "error",
            "error_message": (
                f"Unsupported operation {operation!r}. "
                'Use "add" or "multiply".'
            ),
        }

    return {
        "status": "success",
        "operation": normalized_operation,
        "left": left,
        "right": right,
        "result": result,
    }


root_agent = Agent(
    model=os.getenv("DEMO_AGENT_MODEL", "gemini-2.5-flash"),
    name="demo_time_agent",
    description=(
        "Answers time questions for a small set of world cities and performs "
        "basic addition and multiplication."
    ),
    instruction=(
        "You are a concise, friendly assistant. When the user asks for the "
        "current time in a city, call get_current_time. If the city is not "
        "supported, explain the supported options. When the user asks you to "
        "add or multiply numbers, call calculate."
    ),
    tools=[get_current_time, calculate],
)
