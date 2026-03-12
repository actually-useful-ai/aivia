import requests
import base64
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from requests.exceptions import Timeout, RequestException
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Tools:
    class Valves(BaseModel):
        BASE_URL: str = Field(
            default="https://image.pollinations.ai/prompt/",
            description="Pollinations API URL for text to image generation",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def create_image(
        self,
        prompt: str,
        image_format: str = "default",
        model: Optional[str] = "flux-realism",
        seed: Optional[int] = None,
        nologo: bool = True,
        private: bool = True,
        enhance: bool = True,
        __user__: dict = {},
        __event_emitter__=None,
    ) -> str:
        """
        Creates visually stunning images using the Pollinations.ai API.

        Args:
            prompt: The text prompt to generate the image from
            image_format: Format of the image (default, landscape, portrait, etc.)
            model: The model to use for generation (optional)
            seed: Random seed for reproducible results (optional)
            nologo: Whether to remove the Pollinations logo
            private: Whether to make the generation private
            enhance: Whether to enhance the image quality

        Returns:
            str: Message indicating success or failure
        """
        logger.debug("Starting create_image function")

        try:
            # Define supported image formats
            formats = {
                "default": (1024, 1024),
                "square": (1024, 1024),
                "landscape": (1024, 768),
                "landscape_large": (1440, 1024),
                "portrait": (768, 1024),
                "portrait_large": (1024, 1440),
            }

            logger.debug(f"Validating format: {image_format}")
            if image_format not in formats:
                raise ValueError(
                    f"Invalid format. Must be one of: {', '.join(formats.keys())}"
                )

            width, height = formats[image_format]
            logger.debug(f"Using dimensions: {width}x{height}")

            # Notify start of generation
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Generating image", "done": False},
                }
            )

            # Build the URL with parameters
            encoded_prompt = quote(prompt)
            url = f"{self.valves.BASE_URL}{encoded_prompt}"

            params = {"width": width, "height": height}

            if model:
                params["model"] = model
            if seed is not None:
                params["seed"] = seed
            if nologo:
                params["nologo"] = "true"
            if private:
                params["private"] = "true"
            if enhance:
                params["enhance"] = "true"

            # Make the GET request
            response = requests.get(url, params=params, timeout=(10, 600))

            if response.status_code != 200:
                logger.error(f"API request failed: {response.text}")
                raise RequestException(
                    f"API request failed with status code {response.status_code}"
                )

            # Convert image to base64
            image_content = response.content
            image_url = f"data:image/jpeg;base64,{base64.b64encode(image_content).decode('utf-8')}"

            # Send completion status
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Image generated", "done": True},
                }
            )

            # Send the image
            await __event_emitter__(
                {
                    "type": "message",
                    "data": {
                        "content": f"Generated image for prompt: '{prompt}'\n\n![Generated Image]({image_url})"
                    },
                }
            )

            return f"Image successfully generated for prompt: '{prompt}'"

        except Timeout:
            error_msg = (
                "Request timed out while generating the image. Please try again later."
            )
            logger.error(error_msg)
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": error_msg, "done": True},
                }
            )
            return error_msg

        except RequestException as e:
            error_msg = f"Network error occurred: {str(e)}"
            logger.error(error_msg)
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": error_msg, "done": True},
                }
            )
            return error_msg

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(f"Unexpected error: {str(e)}")
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": error_msg, "done": True},
                }
            )
            return error_msg
