import requests
from typing import Dict, Any, Optional, Callable, Awaitable
from pydantic import BaseModel


class TisaneClient:
    class UserValves(BaseModel):
        """Requires TISANE_PRIMARY API Key"""
        TISANE_PRIMARY: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tisane.ai/parse"

    async def analyze_text(
        self,
        text: str,
        language: str = "en",
        __user__: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> str:
        """
        Analyze text for sentiment, key entities, and offensive content.

        Args:
            text (str): The input text to analyze.
            language (str): The language code (default: "en" for English).

        Returns:
            str: Formatted analysis results.
        """
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Analyzing text with Tisane API...",
                        "done": False,
                    },
                }
            )

        headers = {"Ocp-Apim-Subscription-Key": self.api_key, "Content-Type": "application/json"}
        data = {"language": language, "content": text}

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=15)
            response.raise_for_status()
            analysis = response.json()

            sentiment = analysis.get("sentiment", "Unknown")
            entities = analysis.get("entities", [])
            offenses = analysis.get("offenses", [])

            results = f"Text Analysis Results:\n\n"
            results += f"  Sentiment: {sentiment}\n"
            results += f"  Entities: {', '.join(e['value'] for e in entities)}\n" if entities else "  No key entities found.\n"
            results += f"  Offensive Content: {', '.join(o['group'] for o in offenses)}\n" if offenses else "  No offensive content detected.\n"

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Analysis completed", "done": True},
                    }
                )

            return results

        except requests.RequestException as e:
            error_msg = f"Error analyzing text: {str(e)}"
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
    api_key = "52573597091145c2befcc184c54b49ff"  # Replace with your actual Tisane API key
    tisane_client = TisaneClient(api_key)
    text = "This is a fantastic API, but it sometimes struggles with context."
    import asyncio
    print(asyncio.run(tisane_client.analyze_text(text)))