import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class AirQualityClient:
    class UserValves(BaseModel):
        """Requires AIR_QUALITY_OPEN_DATA API Key"""
        AIR_QUALITY_OPEN_DATA: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.waqi.info/feed"

    async def fetch_air_quality(
        self,
        city: str,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch air quality data for a given city.

        Args:
            city (str): The city to fetch air quality data for.

        Returns:
            str: Formatted air quality report.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching air quality for '{city}'...",
                        "done": False,
                    },
                }
            )

        url = f"{self.base_url}/{city}/?token={self.api_key}"

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "status" in data and data["status"] != "ok":
                return f"Could not retrieve air quality data for '{city}'."

            aqi = data["data"]["aqi"]
            city_name = data["data"]["city"]["name"]
            dominant_pollutant = data["data"].get("dominentpol", "Unknown Pollutant")

            results = f"Air Quality for '{city_name}':\n\n"
            results += f"  AQI (Air Quality Index): {aqi}\n"
            results += f"  Dominant Pollutant: {dominant_pollutant}\n"
            results += f"  More info: {data['data']['city'].get('url', 'No link available')}\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching air quality data: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": error_msg, "done": True}}
                )
            return error_msg


# Example usage:
if __name__ == "__main__":
    api_key = "93eaf4ae2611e5c4576823656e0c82415633c077"  # Replace with your actual Air Quality key
    air_quality_client = AirQualityClient(api_key)
    city = "San Francisco"
    import asyncio
    print(asyncio.run(air_quality_client.fetch_air_quality(city)))