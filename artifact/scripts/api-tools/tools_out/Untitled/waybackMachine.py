
"""
title: Wayback Machine API Integration
author: AI Assistant
version: 1.0
license: MIT
description: A tool that integrates the Wayback Machine API for retrieving archived web pages.
requirements: requests
"""

import os
import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class Tools:
    class Valves(BaseModel):
        API_BASE_URL: str = Field(
            default="https://archive.org/wayback/available",
            description="The base URL for Wayback Machine API"
        )
        USER_AGENT: str = Field(
            default="WaybackMachineAPI/1.0",
            description="User agent string for API requests"
        )

    def __init__(self):
        self.valves = self.Valves()
        self.api_base_url = self.valves.API_BASE_URL
        self.user_agent = self.valves.USER_AGENT

    def get_archived_snapshot(self, url: str, timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve the closest archived snapshot of a given URL from the Wayback Machine.
        :param url: The URL to check for archived snapshots.
        :param timestamp: Optional timestamp to find the closest snapshot (format: YYYYMMDDhhmmss).
        :return: A dictionary containing the response data.
        """
        try:
            params = {"url": url}
            if timestamp:
                params["timestamp"] = timestamp

            headers = {
                "User-Agent": self.user_agent
            }

            response = requests.get(self.api_base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            
            if "archived_snapshots" in data and "closest" in data["archived_snapshots"]:
                snapshot = data["archived_snapshots"]["closest"]
                return {
                    "status": "success",
                    "data": {
                        "available": snapshot["available"],
                        "url": snapshot["url"],
                        "timestamp": snapshot["timestamp"],
                        "status": snapshot["status"]
                    },
                    "original_url": url
                }
            else:
                return {
                    "status": "not_found",
                    "message": "No archived snapshots found for the given URL.",
                    "original_url": url
                }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": str(e),
                "original_url": url
            }

    def get_capture_history(self, url: str) -> Dict[str, Any]:
        """
        Retrieve the capture history for a given URL from the Wayback CDX Server API.
        :param url: The URL to retrieve capture history for.
        :return: A dictionary containing the response data.
        """
        try:
            cdx_api_url = "https://web.archive.org/cdx/search/cdx"
            params = {
                "url": url,
                "output": "json",
                "fl": "timestamp,original,mimetype,statuscode",
                "collapse": "timestamp:8"  # Group by YYYYMMDD
            }

            headers = {
                "User-Agent": self.user_agent
            }

            response = requests.get(cdx_api_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            
            if len(data) > 1:  # First row is the header
                return {
                    "status": "success",
                    "data": [dict(zip(data[0], row)) for row in data[1:]],
                    "original_url": url
                }
            else:
                return {
                    "status": "not_found",
                    "message": "No capture history found for the given URL.",
                    "original_url": url
                }

        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": str(e),
                "original_url": url
            }