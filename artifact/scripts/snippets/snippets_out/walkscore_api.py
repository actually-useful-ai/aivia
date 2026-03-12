import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class WalkScoreClient:
    class UserValves(BaseModel):
        """Requires WALK_SCORE API Key"""
        WALK_SCORE: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.walkscore.com/score"

    async def fetch_walk_score(
        self,
        address: str,
        lat: float,
        lon: float,
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch Walk Score, Transit Score, and Bike Score for a given address.

        Args:
            address (str): The address for which to fetch scores.
            lat (float): Latitude of the location.
            lon (float): Longitude of the location.

        Returns:
            str: Formatted scores including Walk Score, Transit Score, and Bike Score.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching Walk Score for '{address}'...",
                        "done": False,
                    },
                }
            )

        params = {
            "format": "json",
            "address": address,
            "lat": lat,
            "lon": lon,
            "wsapikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if "status" in data and data["status"] != 1:
                return f"Could not retrieve Walk Score for '{address}'."

            results = f"Walkability Scores for '{address}':\n\n"
            results += f"  Walk Score: {data.get('walkscore', 'N/A')} ({data.get('description', 'No description')})\n"
            results += f"  Transit Score: {data.get('transit', {}).get('score', 'N/A')}\n"
            results += f"  Bike Score: {data.get('bike', {}).get('score', 'N/A')}\n"
            results += f"  More info: {data.get('more_info_link', 'No link available')}\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching Walk Score: {str(e)}"
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
    api_key = "61b0834f61254d3dab14e9683a592c7b"  # Replace with your actual Walk Score key
    walkscore_client = WalkScoreClient(api_key)
    address = "1600 Amphitheatre Parkway, Mountain View, CA"
    lat, lon = 37.4221, -122.0841
    import asyncio
    print(asyncio.run(walkscore_client.fetch_walk_score(address, lat, lon)))