import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class MerriamWebsterClient:
    class UserValves(BaseModel):
        """Requires MIRRIAM_WEBSTER_LEARNERS or MIRRIAM_WEBSTER_MEDICAL API Key"""
        MIRRIAM_WEBSTER_LEARNERS: str
        MIRRIAM_WEBSTER_MEDICAL: str

    def __init__(self, learners_key: str, medical_key: str):
        self.learners_key = learners_key
        self.medical_key = medical_key
        self.base_url = "https://www.dictionaryapi.com/api/v3/references/"

    async def fetch_definition(
        self,
        word: str,
        dictionary_type: str = "learners",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Fetch word definitions from Merriam-Webster Dictionary API.

        Args:
            word (str): The word to look up.
            dictionary_type (str): The type of dictionary ("learners" or "medical").

        Returns:
            str: Formatted dictionary entry.
        """
        if dictionary_type == "medical":
            api_key = self.medical_key
            endpoint = "medical/json/"
        else:
            api_key = self.learners_key
            endpoint = "learners/json/"

        url = f"{self.base_url}{endpoint}{word}?key={api_key}"

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching definition for '{word}'...",
                        "done": False,
                    },
                }
            )

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            definitions = response.json()

            if not definitions or isinstance(definitions, list) and not definitions[0]:
                return f"No definition found for '{word}'."

            entry = definitions[0]
            word = entry.get("meta", {}).get("id", word)
            shortdef = entry.get("shortdef", ["No definition available"])

            results = f"Definition of '{word}':\n\n"
            for i, definition in enumerate(shortdef, 1):
                results += f"{i}. {definition}\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Fetch completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error fetching definition: {str(e)}"
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
    learners_key = "d035a35e-5b52-41ea-8823-47002751436b"  # Replace with your actual Learners Dictionary key
    medical_key = "a1ab4851-ebc1-4521-b6e6-5d0465aeec09"  # Replace with your actual Medical Dictionary key
    dictionary_client = MerriamWebsterClient(learners_key, medical_key)
    word = "artificial"
    import asyncio
    print(asyncio.run(dictionary_client.fetch_definition(word)))