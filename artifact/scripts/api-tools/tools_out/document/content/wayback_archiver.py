from typing import Optional, Dict, Any
import requests
import logging
import time
import json
from ...base import BaseTool

class WaybackArchiver(BaseTool):
    """Tool for archiving URLs using the Wayback Machine (Internet Archive)."""
    
    WAYBACK_SAVE_URL = "https://web.archive.org/save/"
    WAYBACK_AVAIL_URL = "https://archive.org/wayback/available?url="
    
    def __init__(self):
        super().__init__()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def submit_url_to_archive(self, url: str) -> Optional[str]:
        """
        Submit a URL to the Wayback Machine and retrieve the archived page link.
        
        Args:
            url (str): The URL to archive
            
        Returns:
            Optional[str]: The archived URL if successful, None otherwise
        """
        self.logger.info(f"Submitting URL to Wayback Machine: {url}")
        
        try:
            # First check if URL is already archived
            avail_response = requests.get(self.WAYBACK_AVAIL_URL + url, headers=self.headers)
            avail_data = avail_response.json()
            
            if avail_data.get('archived_snapshots', {}).get('closest', {}).get('url'):
                self.logger.info("URL already archived")
                return avail_data['archived_snapshots']['closest']['url']

            # If not archived, try to archive it
            save_url = f"{self.WAYBACK_SAVE_URL}{url}"
            self.logger.info(f"Attempting to save URL: {save_url}")
            
            response = requests.get(
                save_url,
                headers=self.headers,
                allow_redirects=True,
                timeout=30
            )
            
            self.logger.debug(f"Save response status: {response.status_code}")
            
            # Wait a moment for archiving to complete
            time.sleep(5)
            
            # Check again for the archived version
            avail_response = requests.get(self.WAYBACK_AVAIL_URL + url, headers=self.headers)
            avail_data = avail_response.json()
            
            if avail_data.get('archived_snapshots', {}).get('closest', {}).get('url'):
                return avail_data['archived_snapshots']['closest']['url']
            
            self.logger.error("Failed to find archived version after save attempt")
            return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error: {str(e)}")
            self.logger.exception(e)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            self.logger.exception(e)
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            self.logger.exception(e)

        return None

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the wayback archiver tool.
        
        Args:
            url (str): The URL to archive
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - success (bool): Whether the operation was successful
                - archived_url (Optional[str]): The archived URL if successful
                - error (Optional[str]): Error message if unsuccessful
        """
        url = kwargs.get('url')
        if not url:
            return {
                'success': False,
                'error': 'No URL provided'
            }
            
        archived_url = self.submit_url_to_archive(url)
        
        if archived_url:
            return {
                'success': True,
                'archived_url': archived_url
            }
        else:
            return {
                'success': False,
                'error': 'Failed to archive URL'
            }

    @property
    def tool_name(self) -> str:
        return "wayback_archiver"

    @property
    def description(self) -> str:
        return "Archives URLs using the Wayback Machine (Internet Archive)"

    @property
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        return {
            "url": {
                "type": "string",
                "description": "The URL to archive",
                "required": True
            }
        } 