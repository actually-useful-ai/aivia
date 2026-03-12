import os
import time
import requests
import json
from datetime import datetime, timedelta, UTC
from atproto import Client

# Credentials and endpoints
BSKY_HANDLE = os.environ['BSKY_HANDLE']
BSKY_PASSWORD = os.environ['BSKY_PASSWORD']

# Determine API endpoint
IS_PRODUCTION = os.environ.get('PRODUCTION', 'false').lower() == 'true'
API_BASE_URL = 'https://api.assisted.space' if IS_PRODUCTION else 'http://localhost:5002'

class SimpleBot:
    def __init__(self):
        self.agent = Client()
        self.login()
        self.processed_notifications = set()
        self.last_checked = datetime.now(UTC).isoformat()
        print(f"Using API endpoint: {API_BASE_URL}")
        
    def login(self):
        print("Logging in...")
        self.agent.login(BSKY_HANDLE, BSKY_PASSWORD)
        print("Login successful.")
        
    def get_notifications(self):
        print("Fetching notifications...")
        response = self.agent.app.bsky.notification.list_notifications()
        print(f"Fetched {len(response.notifications)} notifications.")
        return response.notifications
        
    def get_post_images(self, post):
        """Extract image URLs from a post"""
        try:
            print("Extracting images from post...")
            if hasattr(post, 'embed') and post.embed:
                if hasattr(post.embed, 'images'):
                    images = post.embed.images
                    image_urls = [img.fullsize for img in images]
                    print(f"Found {len(image_urls)} images.")
                    return image_urls
            print("No images found in post.")
            return None
        except Exception as e:
            print(f"Error extracting images: {e}")
            return None

    def get_alt_text(self, image_url):
        """Get alt text from the API"""
        try:
            # Download the image first
            print(f"Downloading image from: {image_url}")
            image_response = requests.get(image_url, timeout=30)
            if not image_response.ok:
                print(f"Failed to download image: {image_response.status_code}")
                raise Exception(f"Failed to download image: {image_response.status_code}")

            # Prepare the file for upload
            files = {
                'file': ('image.jpg', image_response.content, 'image/jpeg')
            }
            
            # Upload to API
            print(f"Uploading image to API: {API_BASE_URL}/upload")
            upload_response = requests.post(
                f"{API_BASE_URL}/upload",
                files=files,
                timeout=30
            )
            
            print(f"Upload response status: {upload_response.status_code}")
            print(f"Upload response content: {upload_response.text}")
            
            if not upload_response.ok:
                raise Exception(f"Failed to upload image: {upload_response.status_code} - {upload_response.text}")
                
            file_id = upload_response.json()['file_id']
            print(f"File uploaded successfully. ID: {file_id}")
            
            # Get alt text from API
            print("Requesting alt text generation...")
            chat_response = requests.post(
                f"{API_BASE_URL}/chat",
                json={
                    "message": "Please describe this image for a visually impaired person.",
                    "file_id": file_id,
                    "bot_id": "7407945108114800645"
                },
                timeout=30,
                stream=True
            )
            
            if not chat_response.ok:
                raise Exception(f"Failed to get alt text: {chat_response.status_code}")

            # Parse the streaming response
            full_text = ""
            for line in chat_response.iter_lines():
                if line:
                    try:
                        data = line.decode('utf-8')
                        if data.startswith("data: "):
                            json_data = json.loads(data[6:])  # Skip "data: " prefix
                            if json_data["type"] == "delta":
                                full_text += json_data["content"]
                            elif json_data["type"] == "complete":
                                break
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error parsing line: {e}")
                        continue

            # Clean up the text before returning
            final_text = full_text.strip()
            print(f"Final alt text: {final_text}")
            return final_text
            
        except Exception as e:
            print(f"Error getting alt text: {str(e)}")
            return f"Failed to generate alt text: {str(e)}"

    def reply_to_mention(self, notification):
        try:
            if notification.uri in self.processed_notifications:
                print(f"Already processed notification from {notification.author.handle}")
                return
                
            print(f"Fetching post thread for notification URI: {notification.uri}")
            thread = self.agent.get_post_thread(notification.uri)
            
            # Check mention post for images
            images = None
            original_image = None
            if hasattr(thread, 'thread') and hasattr(thread.thread, 'post'):
                images = self.get_post_images(thread.thread.post)
                if images:
                    original_image = thread.thread.post.embed.images[0]
                
            # If no images in mention, check parent post
            if not images and hasattr(thread.thread, 'parent'):
                if hasattr(thread.thread.parent, 'post'):
                    images = self.get_post_images(thread.thread.parent.post)
                    if images:
                        original_image = thread.thread.parent.post.embed.images[0]
            
            if images and original_image:
                print(f"Found images: {images}")
                
                # Download the original image
                print(f"Downloading original image from: {original_image.fullsize}")
                image_response = requests.get(original_image.fullsize)
                if not image_response.ok:
                    raise Exception("Failed to download image")
                
                # Get alt text for the image
                alt_text = self.get_alt_text(images[0])
                
                # Upload the image to Bluesky
                print("Uploading image to Bluesky...")
                upload_response = self.agent.com.atproto.repo.upload_blob(
                    image_response.content
                )
                
                # Create the post with both text and image
                self.agent.send_post(
                    text=f"@{notification.author.handle} Alt text generated",
                    facets=[{
                        "index": {
                            "byteStart": 0,
                            "byteEnd": len(f"@{notification.author.handle}")
                        },
                        "features": [{
                            "$type": "app.bsky.richtext.facet#mention",
                            "did": notification.author.did
                        }]
                    }],
                    reply_to={
                        'root': self.get_root_reference(notification),
                        'parent': {
                            'uri': notification.uri,
                            'cid': notification.cid
                        }
                    },
                    embed={
                        '$type': 'app.bsky.embed.images',
                        'images': [{
                            'alt': alt_text,
                            'image': upload_response.blob
                        }]
                    }
                )
                
                self.processed_notifications.add(notification.uri)
                print(f"Successfully processed mention from {notification.author.handle}")
                
        except Exception as e:
            print(f"Error in reply_to_mention: {e}")
            print(f"Notification details: URI={notification.uri}, CID={notification.cid}")
            raise e
    
    def get_root_reference(self, notification):
        """Get the root reference for a reply. If the parent has a root, use that,
        otherwise use the parent as the root."""
        try:
            # Parse the URI to get repo, collection, and rkey
            uri_parts = notification.uri.split('/')
            repo = uri_parts[2]
            collection = uri_parts[3]
            rkey = uri_parts[4]

            # Get the parent post to check if it has a root reference
            parent_post = self.agent.com.atproto.repo.get_record({
                'repo': repo,
                'collection': collection,
                'rkey': rkey
            }).value

            # If parent has a reply with root, use that root
            if 'reply' in parent_post and 'root' in parent_post['reply']:
                return parent_post['reply']['root']
            
            # Otherwise, use the parent as root
            return {
                'uri': notification.uri,
                'cid': notification.cid
            }
        except Exception as e:
            print(f"Error getting root reference: {e}")
            # Fallback to using parent as root
            return {
                'uri': notification.uri,
                'cid': notification.cid
            }
    
    def run(self):
        while True:
            try:
                print("Checking for new notifications...")
                notifications = self.get_notifications()
                
                for notif in notifications:
                    if hasattr(notif, 'indexed_at') and notif.indexed_at < self.last_checked:
                        continue
                        
                    if notif.reason == 'mention':
                        try:
                            print(f"\nProcessing mention from: {notif.author.handle}")
                            print(f"Notification URI: {notif.uri}")
                            print(f"Notification CID: {notif.cid}")
                            self.reply_to_mention(notif)
                            print("Reply sent successfully")
                        except Exception as e:
                            print(f"Error replying to mention: {str(e)}")
                            continue
                
                if notifications:
                    newest_notification = notifications[0]
                    if hasattr(newest_notification, 'indexed_at'):
                        self.last_checked = newest_notification.indexed_at
                    
                time.sleep(10)
                
            except Exception as e:
                print(f"Main loop error: {str(e)}")
                time.sleep(20)
                self.login()

if __name__ == "__main__":
    bot = SimpleBot()
    bot.run() 