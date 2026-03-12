"""
title: BBC News Feed
author: @nathanwindisch, with bug fixes by @igna503
author_url: https://github.com/nathanwindisch, https://github.com/igna503
funding_url: https://www.patreon.com/NathanWindisch
version: 0.1.0
changelog:
- 0.0.1 - Initial upload to openwebui community.
- 0.0.2 - Modified formatting slightly.
- 0.0.3 - Added tool docstring, and this changelog.
- 0.0.4 - Added funding_url to docstring.
- 0.0.5 - Updated get_bbc_news_feed function to use a default for 
          the ArticleType, and updated it's docstring to include 
          a list of the possible types, to assist the LLM's query.
- 0.0.6 - Added event emitter to the get_bbc_news_feed function, 
          to provide status updates to the user as the function 
          executes. Also wrapped the function in a try/catch, to 
          handle any exceptions that may occur during execution.
- 0.0.7 - Fixed a major bug where the type was not being casted 
          to the ArticleType enum, causing the get_uri function 
          to not be called correctly.
- 0.0.8 - Updated the ArticleType parameter docstring to make it 
          mandatory, and for to contain the full names of the
          'world/' types rather than the abbreviations.
- 0.0.9 - Created a new function, get_bbc_news_content, which 
          retrieves the article text content of a BBC News link, 
          given it's URI.
- 0.1.0 - Removed enum, used dict instead, fixing bug where
          articletype was not a supported JSON schema by
          Open WebUI.
"""

import re
import json
import requests
import xml.etree.ElementTree as ElementTree
from typing import Awaitable, Callable
from pydantic import BaseModel
from bs4 import BeautifulSoup


categories = {
    "top_stories": "",
    "world": "world",
    "uk": "uk",
    "business": "business",
    "politics": "politics",
    "health": "health",
    "education": "education",
    "science_and_environment": "science_and_environment",
    "technology": "technology",
    "entertainment_and_arts": "entertainment_and_arts",
    "england": "england",
    "northern_ireland": "northern_ireland",
    "scotland": "scotland",
    "wales": "wales",
    "africa": "world/africa",
    "asia": "world/asia",
    "australia": "world/australia",
    "europe": "world/europe",
    "latin_america": "world/latin_america",
    "middle_east": "world/middle_east",
    "us_and_canada": "world/us_and_canada",
}


def get_name(category) -> str:
    return category.replace("_", " ").title()


def get_uri(category) -> str:
    return (
        f"https://feeds.bbci.co.uk/news/{categories[category]}/rss.xml"
        if category != "top_stories"
        else "https://feeds.bbci.co.uk/news/rss.xml"
    )


# Regex to match a BBC News article URI.
# Details:
#  - Must use http or https.
#  - Must be a bbc.com or bbc.co.uk domain.
#  - Must be a news article or video.
#  - Must have a valid ID (alphanumeric characters).
URI_REGEX = re.compile(
    "^(https?:\/\/)(www\.)?bbc\.(com|co\.uk)\/news\/(articles|videos)\/\w+$"
)


class Tools:
    def __init__(self):
        pass

    class UserValves(BaseModel):
        pass

    async def get_bbc_news_feed(
        self,
        category: str,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        __user__: dict = {},
    ) -> str:
        """
        Get the latest news from the BBC, as an array of JSON objects with a title, description, link, and published date.
        :param category: The category of news to get. It can be any of the 'categories' dict's keys (world, uk, business, politics, health, education, science_and_environment, technology, entertainment_and_arts, england, northern_ireland, scotland, wales, world/africa, world/asia, world/australia, world/europe, world/latin_america, world/middle_east, world/us_and_canada).
        :return: A list of news items or an error message.
        """
        await __event_emitter__(
            {
                "data": {
                    "description": f"Starting BBC News Feed retrieval for articles in the '{get_name(category)}' category...",
                    "status": "in_progress",
                    "done": False,
                },
                "type": "status",
            }
        )
        output = []
        try:
            response = requests.get(get_uri(category))
            if not response.ok:
                return f"Error: '{category}' ({get_uri(category)}) not found ({response.status_code})"
            root = ElementTree.fromstring(response.content)
            for item in root.iter("item"):
                output.append(
                    {
                        "title": item.find("title").text,
                        "description": item.find("description").text,
                        "link": item.find("link").text,
                        "published": item.find("pubDate").text,
                    }
                )
            await __event_emitter__(
                {
                    "data": {
                        "description": f"Retrieved {len(output)} news items from BBC News Feed for articles in the '{get_name(category)}' category.",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                }
            )
        except Exception as e:
            await __event_emitter__(
                {
                    "data": {
                        "description": f"Failed to retrieved any news items from BBC News Feed for articles in the '{get_name(category)}' ({get_uri(category)}) category: {e}.",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                }
            )
            return f"Error: {e}"

        return json.dumps(output)

    async def get_bbc_news_content(
        self,
        uri: str,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        __user__: dict = {},
    ) -> str:
        """
        Get the content of a news article from the BBC.
        :param uri: The URI of the article to get the content of, which should start with https://bbc.com/news or https://bbc.co.uk/news.
        :return: The content of the article or an error message.
        """
        await __event_emitter__(
            {
                "data": {
                    "description": f"Starting BBC News Article retrieval from '{uri}'...",
                    "status": "in_progress",
                    "done": False,
                },
                "type": "status",
            }
        )

        if uri == "":
            await __event_emitter__(
                {
                    "data": {
                        "description": f"Error: No URI provided.",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                }
            )
            return "Error: No URI provided"

        if not re.match(URI_REGEX, uri):
            await __event_emitter__(
                {
                    "data": {
                        "description": f"Error: URI must be a BBC News article.",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                }
            )
            return "Error: URI must be a BBC News article."

        content = ""
        try:
            response = requests.get(uri)
            if not response.ok:
                return f"Error: '{uri}' not found ({response.status_code})"
            article = BeautifulSoup(response.content, "html.parser").find("article")
            if article is None:
                await __event_emitter__(
                    {
                        "data": {
                            "description": f"Failed to retrieve BBC News Article content from '{uri}': Article content not found.",
                            "status": "complete",
                            "done": True,
                        },
                        "type": "status",
                    }
                )
                return f"Error: Article content for {uri} not found."

            paragraphs = article.find_all("p")
            for paragraph in paragraphs:
                content += f"{paragraph.text}\n"
            await __event_emitter__(
                {
                    "data": {
                        "description": f"Retrieved BBC News Article content from '{uri}' ({len(content)} characters).",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                }
            )
        except Exception as e:
            await __event_emitter__(
                {
                    "data": {
                        "description": f"Failed to retrieve BBC News Article content from '{uri}': {e}.",
                        "status": "complete",
                        "done": True,
                    },
                    "type": "status",
                }
            )
            return f"Error: {e}"

        return content
