#!/usr/bin/env python
"""
Coze API Chat Implementation for Flask
This module provides a Flask interface to the Coze API for streaming chat responses.
Supports model selection, conversation history, and image handling.
"""

import os
import sys
import tempfile
import io
import json
import requests
from flask import Flask, request, render_template_string, Response, jsonify, stream_with_context
from typing import Generator, List, Dict, Optional, Union
from datetime import datetime
from base64 import b64encode
from PIL import Image
import logging
import traceback
from huggingface_hub import InferenceClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
COZE_AUTH_TOKEN = 'pat_AfJwWFTQ9q0CpE0TDhNOMLELn5kC9MsVr4jYSrudZZw1B5BdlszXQoNOrWTALe91'
COZE_BOT_ID = "7462296933429346310"  # Alt Text Generator bot ID
COZE_TTS_BOT_ID = "7463319430379470854"  # TTS Generator bot ID
COZE_SPACE_ID = "7345427862138912773"
HF_API_KEY = "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"

# Store for conversations
conversation_store = {}

# Import Coze SDK
try:
    from cozepy import Coze, TokenAuth, Message, ChatEventType, MessageObjectString
    if not COZE_AUTH_TOKEN:
        logger.warning("COZE_AUTH_TOKEN not found in environment variables")
        coze = None
    else:
        logger.info("Initializing Coze client")
        coze = Coze(auth=TokenAuth(token=COZE_AUTH_TOKEN))
except Exception as e:
    logger.error(f"Failed to initialize Coze client: {str(e)}")
    coze = None

# Define the stream_chat_with_file function before it's used
def stream_chat_with_file(message, bot_id, user_id, file_id=None):
    """Stream a chat response from Coze with proper file handling."""
    try:
        # Initialize conversation if needed
        if user_id not in conversation_store:
            conversation_store[user_id] = {}

        if bot_id not in conversation_store[user_id]:
            initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
            conversation = coze.conversations.create(messages=[initial_message])
            conversation_store[user_id][bot_id] = conversation.id

        conversation_id = conversation_store[user_id][bot_id]

        # Build message with optional file attachment
        messages = []
        if file_id:
            messages.append(
                Message.build_user_question_objects([
                    MessageObjectString.build_text(message or "Please describe this image"),
                    MessageObjectString.build_image(file_id=file_id)
                ])
            )
        else:
            messages.append(Message.build_user_question_text(message))

        # Stream response
        total_tokens = 0
        for event in coze.chat.stream(
            bot_id=bot_id,
            user_id=user_id,
            conversation_id=conversation_id,
            additional_messages=messages
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                total_tokens += len(event.message.content.split())
                yield {
                    'type': 'delta',
                    'content': event.message.content,
                    'tokens': total_tokens
                }
            elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                yield {
                    'type': 'complete',
                    'tokens': total_tokens
                }

    except Exception as e:
        logger.error(f"Error in stream_chat_response: {str(e)}")
        yield {'type': 'error', 'message': str(e)}

class CozeChat:
    """Wrapper class for Coze API chat functionality."""

    def __init__(self, coze_client=None, auth_token=None):
        """Initialize with Coze client and API key."""
        self.coze = coze_client
        self.auth_token = auth_token
        self.conversation_store = {}

    def fetch_coze_bots(self):
        """Fetch bots from Coze API using direct HTTP request."""
        try:
            if not self.auth_token:
                logger.warning("No auth token available for fetching Coze bots")
                return []
                
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Try various possible endpoint patterns
            endpoints = [
                "https://api.coze.com/v1/published_bots",
                "https://api.coze.com/v1/bots",
                "https://api.coze.com/v1/bots/list",
                "https://api.coze.com/v1/bots/published",
                "https://api.coze.com/v1/agents",
                "https://www.coze.com/api/v1/bots",
                "https://www.coze.com/api/v1/published_bots"
            ]
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Attempting to fetch bots from: {endpoint}")
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    
                    # Only raise for 4xx/5xx status codes, not for other types of errors
                    response.raise_for_status()
                    
                    # Try to parse the response as JSON
                    data = response.json()
                    
                    # Check common response patterns
                    if isinstance(data, list) and len(data) > 0:
                        logger.info(f"Successfully fetched {len(data)} bots from {endpoint}")
                        return data
                    elif "data" in data and isinstance(data["data"], list):
                        logger.info(f"Successfully fetched {len(data['data'])} bots from {endpoint}")
                        return data["data"]
                    elif "bots" in data and isinstance(data["bots"], list):
                        logger.info(f"Successfully fetched {len(data['bots'])} bots from {endpoint}")
                        return data["bots"]
                    elif "results" in data and isinstance(data["results"], list):
                        logger.info(f"Successfully fetched {len(data['results'])} bots from {endpoint}")
                        return data["results"]
                    else:
                        logger.warning(f"Received unexpected response structure from {endpoint}")
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request to {endpoint} failed: {str(e)}")
                except ValueError as e:
                    logger.warning(f"Failed to parse JSON from {endpoint}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Unexpected error accessing {endpoint}: {str(e)}")
            
            # If space ID is available, try the space bots endpoints
            if COZE_SPACE_ID:
                space_endpoints = [
                    f"https://api.coze.com/v1/spaces/{COZE_SPACE_ID}/bots",
                    f"https://api.coze.com/v1/spaces/{COZE_SPACE_ID}/agents",
                    f"https://www.coze.com/api/v1/spaces/{COZE_SPACE_ID}/bots"
                ]
                
                for endpoint in space_endpoints:
                    try:
                        logger.info(f"Attempting to fetch bots from space endpoint: {endpoint}")
                        response = requests.get(endpoint, headers=headers, timeout=10)
                        response.raise_for_status()
                        
                        data = response.json()
                        
                        # Check common response patterns
                        if isinstance(data, list) and len(data) > 0:
                            logger.info(f"Successfully fetched {len(data)} space bots from {endpoint}")
                            return data
                        elif "data" in data and isinstance(data["data"], list):
                            logger.info(f"Successfully fetched {len(data['data'])} space bots from {endpoint}")
                            return data["data"]
                        elif "bots" in data and isinstance(data["bots"], list):
                            logger.info(f"Successfully fetched {len(data['bots'])} space bots from {endpoint}")
                            return data["bots"]
                        elif "results" in data and isinstance(data["results"], list):
                            logger.info(f"Successfully fetched {len(data['results'])} space bots from {endpoint}")
                            return data["results"]
                    except Exception as e:
                        logger.warning(f"Failed to fetch space bots from {endpoint}: {str(e)}")
            
            # If all attempts failed, log and return empty list
            logger.warning("Could not fetch bots from any endpoint. The API endpoints may have changed or access might be restricted.")
            logger.info("Falling back to hardcoded models only")
            return []
            
        except Exception as e:
            logger.error(f"Error in fetch_coze_bots: {str(e)}")
            logger.error(traceback.format_exc())
            return []

    def list_models(
        self,
        sort_by: str = "created",
        page: int = 1,
        page_size: int = 5,
        capability_filter: Optional[str] = None
    ) -> List[Dict]:
        """Return a list of available Coze bots."""
        try:
            # Always include the hardcoded Alt Text Generator bot
            models = [{
                "id": COZE_BOT_ID,
                "name": "Alt Text Generator",
                "description": "Coze bot for generating alt text",
                "capabilities": ["text", "vision"],
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "owned_by": "coze"
            }]
            
            # Attempt to fetch additional bots dynamically
            if self.auth_token:
                try:
                    # Fetch bots from the API
                    bots = self.fetch_coze_bots()
                    logger.info(f"Fetched {len(bots)} bots from Coze API")
                    
                    # Process each bot and add to the models list
                    for bot in bots:
                        # Skip if the bot data is not a dict
                        if not isinstance(bot, dict):
                            logger.warning(f"Skipping bot with non-dict data: {bot}")
                            continue
                            
                        # Extract bot ID using various potential field names
                        bot_id = None
                        for id_field in ['id', 'botId', 'bot_id', 'uuid', 'identifier']:
                            if id_field in bot:
                                bot_id = bot.get(id_field)
                                break
                                
                        if not bot_id:
                            logger.warning(f"Skipping bot with no identifiable ID: {bot}")
                            continue
                            
                        # Skip the alt text bot since we already have it hardcoded
                        if bot_id == COZE_BOT_ID:
                            continue
                        
                        # Extract bot details using various potential field names
                        bot_name = None
                        for name_field in ['name', 'botName', 'bot_name', 'title', 'displayName']:
                            if name_field in bot:
                                bot_name = bot.get(name_field)
                                if bot_name:
                                    break
                        
                        bot_name = bot_name or f"Bot {bot_id}"
                        
                        bot_desc = None
                        for desc_field in ['description', 'desc', 'about', 'summary', 'info']:
                            if desc_field in bot:
                                bot_desc = bot.get(desc_field)
                                if bot_desc:
                                    break
                                    
                        bot_desc = bot_desc or f"Coze bot {bot_id}"
                        
                        # Determine capabilities by checking common field patterns
                        bot_capabilities = ["text"]  # Assume all bots support text
                        
                        # Check for vision capabilities with various field patterns
                        vision_indicators = [
                            bot.get('has_vision', False),
                            bot.get('hasVision', False),
                            bot.get('vision_enabled', False),
                            bot.get('visionEnabled', False),
                            bot.get('supportsVision', False),
                            bot.get('supports_vision', False),
                            bot.get('supports_images', False),
                            bot.get('supportsImages', False),
                            'vision' in bot.get('capabilities', []),
                            'image' in bot.get('capabilities', [])
                        ]
                        
                        if any(vision_indicators):
                            bot_capabilities.append("vision")
                            
                        # Check for audio capabilities with various field patterns
                        audio_indicators = [
                            bot.get('has_audio', False),
                            bot.get('hasAudio', False),
                            bot.get('audio_enabled', False),
                            bot.get('audioEnabled', False),
                            bot.get('supportsAudio', False),
                            bot.get('supports_audio', False),
                            'audio' in bot.get('capabilities', []),
                            'voice' in bot.get('capabilities', [])
                        ]
                        
                        if any(audio_indicators):
                            bot_capabilities.append("audio")
                        
                        # Extract creation date if available
                        creation_date = datetime.now().strftime("%Y-%m-%d")
                        for date_field in ['created_at', 'createdAt', 'creation_date', 'creationDate', 'created']:
                            if date_field in bot:
                                date_value = bot.get(date_field)
                                if date_value:
                                    try:
                                        # Handle different date formats - string or timestamp
                                        if isinstance(date_value, str):
                                            creation_date = date_value
                                        elif isinstance(date_value, (int, float)):
                                            # Convert timestamp to date string
                                            creation_date = datetime.fromtimestamp(date_value).strftime("%Y-%m-%d")
                                    except Exception as e:
                                        logger.warning(f"Failed to parse creation date: {e}")
                                    break
                        
                        # Extract owner information if available
                        owner = "coze"
                        for owner_field in ['owner', 'owned_by', 'ownedBy', 'creator', 'author']:
                            if owner_field in bot:
                                owner_value = bot.get(owner_field)
                                if owner_value:
                                    owner = owner_value
                                    break
                        
                        # Add bot to models list
                        models.append({
                            "id": bot_id,
                            "name": bot_name,
                            "description": bot_desc,
                            "capabilities": bot_capabilities,
                            "created_at": creation_date,
                            "owned_by": owner
                        })
                        
                    logger.info(f"Added {len(models) - 1} additional Coze bots")
                except Exception as e:
                    logger.error(f"Error processing Coze bots: {str(e)}")
                    logger.error(traceback.format_exc())
                    # Fall back to including the TTS bot if dynamic fetching fails
                    if not any(m["id"] == COZE_TTS_BOT_ID for m in models):
                        models.append({
                            "id": COZE_TTS_BOT_ID,
                            "name": "TTS Generator",
                            "description": "Coze bot for text-to-speech",
                            "capabilities": ["text", "audio"],
                            "created_at": datetime.now().strftime("%Y-%m-%d"),
                            "owned_by": "coze"
                        })
            else:
                # If auth token is not available, add the hardcoded TTS bot
                models.append({
                    "id": COZE_TTS_BOT_ID,
                    "name": "TTS Generator",
                    "description": "Coze bot for text-to-speech",
                    "capabilities": ["text", "audio"],
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "owned_by": "coze"
                })
            
            # Apply capability filter
            if capability_filter:
                models = [m for m in models if capability_filter in m["capabilities"]]
                
            # Apply pagination
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            return models[start_idx:end_idx]
        except Exception as e:
            logger.error(f"Error in list_models: {str(e)}")
            logger.error(traceback.format_exc())
            # Return default models in case of error
            return [{
                "id": COZE_BOT_ID,
                "name": "Alt Text Generator",
                "description": "Coze bot for generating alt text",
                "capabilities": ["text", "vision"],
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "owned_by": "coze"
            }]

    def stream_chat_response(
        self,
        message: str,
        model: str = COZE_BOT_ID,
        user_id: str = "default_user",
        file_id: Optional[str] = None
    ) -> Generator[Dict, None, None]:
        """Stream a chat response from Coze using the shared implementation."""
        # Use the global conversation store for compatibility
        global conversation_store
        
        # Initialize user in global conversation store if needed
        if user_id not in conversation_store:
            conversation_store[user_id] = {}
            
        # Initialize user in local store for compatibility with class methods
        if user_id not in self.conversation_store:
            self.conversation_store[user_id] = {}
            
        # Make sure conversation is initialized in both stores
        if model not in conversation_store[user_id]:
            initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
            conversation = self.coze.conversations.create(messages=[initial_message])
            conversation_store[user_id][model] = conversation.id
            # Also update local store
            self.conversation_store[user_id][model] = conversation_store[user_id][model]
        
        # Use the shared implementation
        yield from stream_chat_with_file(message, model, user_id, file_id)

    def clear_conversation(self, user_id: str, model: str):
        """Clear conversation history."""
        # Clear from global conversation store
        global conversation_store
        if user_id in conversation_store and model in conversation_store[user_id]:
            del conversation_store[user_id][model]
            
        # Also clear from local store
        if user_id in self.conversation_store and model in self.conversation_store[user_id]:
            del self.conversation_store[user_id][model]

# Initialize the chat client with the global coze client
chat_client = CozeChat(coze_client=coze, auth_token=COZE_AUTH_TOKEN) if coze else None

# Flask routes
app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coze Chat</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            background-color: #f5f5f7;
        }
        header {
            background-color: #333;
            color: white;
            padding: 1rem;
            text-align: center;
        }
        main {
            display: flex;
            flex-direction: column;
            flex: 1;
            padding: 1rem;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 1rem;
        }
        button {
            padding: 8px 16px;
            background-color: #0071e3;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background-color: #0062c3;
        }
        #clearBtn {
            background-color: #ff3b30;
        }
        #clearBtn:hover {
            background-color: #d33227;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            flex: 1;
            gap: 10px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 1rem;
            overflow-y: auto;
            max-height: 60vh;
        }
        .message {
            padding: 12px;
            border-radius: 8px;
            max-width: 80%;
            word-break: break-word;
        }
        .user-message {
            background-color: #e1f5fe;
            align-self: flex-end;
        }
        .assistant-message {
            background-color: #f1f1f1;
            align-self: flex-start;
        }
        .input-area {
            display: flex;
            gap: 10px;
            margin-top: 1rem;
        }
        #userInput {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .bot-selector {
            margin-bottom: 1rem;
        }
        select, .file-input-label {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
            font-size: 14px;
        }
        .file-input-container {
            position: relative;
            overflow: hidden;
            display: inline-block;
        }
        .file-input-label {
            cursor: pointer;
            display: inline-block;
            padding: 8px 16px;
            background-color: #34c759;
            color: white;
            border-radius: 4px;
        }
        .file-input-label:hover {
            background-color: #2aa84a;
        }
        #fileInput {
            position: absolute;
            left: 0;
            top: 0;
            opacity: 0;
            width: 0.1px;
            height: 0.1px;
        }
        #uploadPreview {
            max-width: 200px;
            max-height: 200px;
            margin-top: 10px;
            display: none;
            border-radius: 4px;
        }
        .loading {
            display: none;
            align-items: center;
            justify-content: center;
            margin-top: 10px;
        }
        .loading-spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #0071e3;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error {
            color: #ff3b30;
            padding: 10px;
            background-color: #ffeeee;
            border-radius: 4px;
            margin-top: 10px;
            display: none;
        }
    </style>
</head>
<body>
    <header>
        <h1>Coze Chat</h1>
    </header>
    <main>
        <div class="bot-selector">
            <label for="botSelect">Select Bot:</label>
            <select id="botSelect">
                <option value="{{ alt_text_bot }}">Alt Text Generator</option>
                <option value="{{ tts_bot }}">TTS Generator</option>
            </select>
        </div>
        
        <div class="chat-container" id="chatContainer"></div>
        
        <div class="loading" id="loadingIndicator">
            <div class="loading-spinner"></div>
            <span>Processing...</span>
        </div>
        
        <div class="error" id="errorContainer"></div>
        
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your message...">
            <div class="file-input-container">
                <label for="fileInput" class="file-input-label">Upload</label>
                <input type="file" id="fileInput" accept="image/*">
            </div>
            <button id="sendBtn">Send</button>
            <button id="clearBtn">Clear</button>
        </div>
        
        <img id="uploadPreview" src="" alt="Preview">
    </main>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');
        const fileInput = document.getElementById('fileInput');
        const sendBtn = document.getElementById('sendBtn');
        const clearBtn = document.getElementById('clearBtn');
        const botSelect = document.getElementById('botSelect');
        const uploadPreview = document.getElementById('uploadPreview');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const errorContainer = document.getElementById('errorContainer');
        
        let uploadedFileId = null;
        let currentUserId = 'user_' + Date.now();
        
        // Handle file selection
        fileInput.addEventListener('change', async function(e) {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                
                // Preview image
                const reader = new FileReader();
                reader.onload = function(e) {
                    uploadPreview.src = e.target.result;
                    uploadPreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
                
                // Upload file
                await uploadFile(file);
            }
        });
        
        // Upload file to server
        async function uploadFile(file) {
            try {
                loadingIndicator.style.display = 'flex';
                errorContainer.style.display = 'none';
                
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success && data.file_id) {
                    uploadedFileId = data.file_id;
                    console.log('File uploaded successfully, ID:', uploadedFileId);
                } else {
                    throw new Error(data.error || 'Unknown error uploading file');
                }
            } catch (error) {
                console.error('Error uploading file:', error);
                showError('Error uploading file: ' + error.message);
                uploadedFileId = null;
                uploadPreview.style.display = 'none';
            } finally {
                loadingIndicator.style.display = 'none';
            }
        }
        
        // Send message
        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
        
        async function sendMessage() {
            const message = userInput.value.trim();
            const botId = botSelect.value;
            
            if (!message && !uploadedFileId) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            
            // Clear input
            userInput.value = '';
            
            try {
                loadingIndicator.style.display = 'flex';
                errorContainer.style.display = 'none';
                
                // Prepare request data
                const requestData = {
                    message: message,
                    bot_id: botId,
                    user_id: currentUserId
                };
                
                if (uploadedFileId) {
                    requestData.file_id = uploadedFileId;
                }
                
                // Use EventSource for streaming response
                const source = new EventSource(
                    '/chat_unified?' + 
                    new URLSearchParams({
                        message: message,
                        bot_id: botId,
                        user_id: currentUserId,
                        ...(uploadedFileId ? { file_id: uploadedFileId } : {})
                    })
                );
                
                let assistantMessage = '';
                let assistantDiv = null;
                
                source.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'start') {
                        // Create assistant message div
                        assistantDiv = document.createElement('div');
                        assistantDiv.className = 'message assistant-message';
                        chatContainer.appendChild(assistantDiv);
                    } else if (data.type === 'delta') {
                        // Update assistant message with new content
                        assistantMessage += data.content;
                        if (assistantDiv) {
                            assistantDiv.textContent = assistantMessage;
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }
                    } else if (data.type === 'complete') {
                        // Message complete
                        source.close();
                        loadingIndicator.style.display = 'none';
                    } else if (data.type === 'error') {
                        // Handle error
                        source.close();
                        showError('Error: ' + data.message);
                    }
                };
                
                source.onerror = function(error) {
                    source.close();
                    console.error('EventSource error:', error);
                    showError('Connection error occurred');
                    loadingIndicator.style.display = 'none';
                };
                
                // Reset file upload
                uploadedFileId = null;
                uploadPreview.style.display = 'none';
                fileInput.value = '';
                
            } catch (error) {
                console.error('Error sending message:', error);
                showError('Error: ' + error.message);
                loadingIndicator.style.display = 'none';
            }
        }
        
        // Add message to chat
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text || (sender === 'user' ? 'Please analyze this image' : '');
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // Show error message
        function showError(message) {
            errorContainer.textContent = message;
            errorContainer.style.display = 'block';
        }
        
        // Clear chat
        clearBtn.addEventListener('click', async function() {
            try {
                loadingIndicator.style.display = 'flex';
                errorContainer.style.display = 'none';
                
                const response = await fetch('/clear', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: currentUserId,
                        bot_id: botSelect.value
                    })
                });
                
                if (response.ok) {
                    chatContainer.innerHTML = '';
                    uploadedFileId = null;
                    uploadPreview.style.display = 'none';
                    fileInput.value = '';
                } else {
                    const data = await response.json();
                    throw new Error(data.error || 'Failed to clear chat');
                }
            } catch (error) {
                console.error('Error clearing chat:', error);
                showError('Error clearing chat: ' + error.message);
            } finally {
                loadingIndicator.style.display = 'none';
            }
        });
    </script>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def default_chat():
    """Default endpoint for Coze chat completions."""
    if request.method == "GET":
        return render_template_string(
            HTML_TEMPLATE,
            alt_text_bot=COZE_BOT_ID,
            tts_bot=COZE_TTS_BOT_ID
        )
        
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        message = data.get('message', '')
        file_id = data.get('file_id')
        user_id = data.get('user_id', 'default_user')
        bot_id = data.get('bot_id', COZE_BOT_ID)

        def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
                
                for response in chat_client.stream_chat_response(
                    message=message,
                    model=bot_id,
                    user_id=user_id,
                    file_id=file_id
                ):
                    yield f"data: {json.dumps(response)}\n\n"

            except Exception as e:
                logger.error(f"Error in default chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    except Exception as e:
        logger.error(f"Error in default chat: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route("/completions", methods=["POST"])
def completions_chat():
    """Endpoint for Coze chat completions."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        message = data.get('message', '')
        file_id = data.get('file_id')
        user_id = data.get('user_id', 'default_user')
        bot_id = data.get('bot_id', COZE_BOT_ID)

        def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
                
                for response in chat_client.stream_chat_response(
                    message=message,
                    model=bot_id,
                    user_id=user_id,
                    file_id=file_id
                ):
                    yield f"data: {json.dumps(response)}\n\n"

            except Exception as e:
                logger.error(f"Error in completions chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    except Exception as e:
        logger.error(f"Error in completions chat: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route("/drummer", methods=["POST"])
def drummer_chat():
    """Endpoint for Coze drummer chat completions."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        message = data.get('message', '')
        file_id = data.get('file_id')
        user_id = data.get('user_id', 'default_user')
        bot_id = data.get('bot_id', COZE_BOT_ID)

        def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
                
                for response in chat_client.stream_chat_response(
                    message=message,
                    model=bot_id,
                    user_id=user_id,
                    file_id=file_id
                ):
                    yield f"data: {json.dumps(response)}\n\n"

            except Exception as e:
                logger.error(f"Error in drummer chat stream: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream'
        )
    except Exception as e:
        logger.error(f"Error in drummer chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/hf", methods=["POST"])
def hf_chat():
    """Endpoint for Hugging Face inference API chat completions."""
    try:
        if not HF_API_KEY:
            return jsonify({"error": "Hugging Face API key not configured"}), 500

        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        client = InferenceClient(api_key=HF_API_KEY)
        
        # Extract parameters
        message = data.get('message', '')
        image_data = data.get('image')  # Expecting base64 encoded image
        model = data.get('model', 'meta-llama/Llama-3.2-11B-Vision-Instruct')
        max_tokens = data.get('max_tokens', 500)
        
        # Prepare messages
        messages = []
        if image_data:
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message or "Describe this image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            }]
        else:
            messages = [{
                "role": "user",
                "content": message
            }]

        def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
                
                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens
                )
                
                response_content = completion.choices[0].message.content
                total_tokens = len(response_content.split())
                
                yield f"data: {json.dumps({
                    'type': 'delta',
                    'content': response_content,
                    'tokens': total_tokens
                })}\n\n"
                
                yield f"data: {json.dumps({
                    'type': 'complete',
                    'tokens': total_tokens
                })}\n\n"
                
            except Exception as e:
                logger.error(f"Error in HF chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"Error in HF chat: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route("/clear", methods=["POST"])
def clear_conversation():
    """Clear a chat conversation."""
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        bot_id = data.get('bot_id', COZE_BOT_ID)
        
        chat_client.clear_conversation(user_id, bot_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file uploads for Coze."""
    logger.info("File upload endpoint hit")
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if not file:
            return jsonify({"error": "Empty file"}), 400

        # Upload file using direct API call
        files = {'file': (file.filename, file.stream, file.content_type)}
        headers = {'Authorization': f'Bearer {COZE_AUTH_TOKEN}'}
        
        logger.info(f"Uploading file {file.filename} to Coze")
        upload_response = requests.post(
            'https://api.coze.com/v1/files/upload',
            files=files,
            headers=headers
        )
        
        logger.info(f"Upload response: {upload_response.text}")
        
        if not upload_response.ok:
            raise Exception(f"Upload failed: {upload_response.text}")
            
        upload_data = upload_response.json()
        logger.info(f"Upload data: {upload_data}")
        
        # Extract file ID according to documented response format
        # Response format: {"code": 0, "data": {"id": "xxx", ...}, "msg": ""}
        file_id = None
        if upload_data.get('code') == 0:
            file_id = upload_data.get('data', {}).get('id')
        
        if not file_id:
            raise Exception("No file_id in response")
        
        logger.info(f"File uploaded successfully, ID: {file_id}")
        return jsonify({
            "success": True,
            "file_id": file_id
        })

    except Exception as e:
        error_msg = str(e)
        logger.error(f"File upload error: {error_msg}")
        return jsonify({"error": error_msg}), 500

@app.route("/chat", methods=["GET", "POST"])
def chat():
    """Handle chat requests and file uploads."""
    if request.method == "GET":
        # Handle SSE request
        message = request.args.get('message', '')
        bot_id = request.args.get('bot_id', COZE_BOT_ID)
        user_id = request.args.get('user_id', 'default_user')

        def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
                
                for response in chat_client.stream_chat_response(
                    message=message,
                    model=bot_id,
                    user_id=user_id
                ):
                    yield f"data: {json.dumps(response)}\n\n"

            except Exception as e:
                logger.error(f"Error in chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    else:
        # Handle POST request with file upload
        try:
            message = request.form.get('message', '')
            bot_id = request.form.get('bot_id', COZE_BOT_ID)
            user_id = request.form.get('user_id', 'default_user')
            file_id = None

            if 'file' in request.files:
                file = request.files['file']
                if file:
                    # Save file temporarily
                    temp_dir = tempfile.gettempdir()
                    temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png")
                    try:
                        file.save(temp_file.name)
                        temp_file.close()
                        
                        # Upload file to Coze
                        file_id = chat_client.coze.files.upload(temp_file.name)
                    finally:
                        try:
                            os.remove(temp_file.name)
                        except Exception as cleanup_error:
                            logger.error(f"Error cleaning up temporary file: {cleanup_error}")

            def generate():
                try:
                    yield f"data: {json.dumps({'type': 'start'})}\n\n"
                    
                    for response in chat_client.stream_chat_response(
                        message=message,
                        model=bot_id,
                        user_id=user_id,
                        file_id=file_id
                    ):
                        yield f"data: {json.dumps(response)}\n\n"

                except Exception as e:
                    logger.error(f"Error in chat stream: {str(e)}\n{traceback.format_exc()}")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

            return Response(
                stream_with_context(generate()),
                content_type='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'X-Accel-Buffering': 'no'
                }
            )
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}\n{traceback.format_exc()}")
            return jsonify({"error": str(e)}), 500

@app.route("/chat_unified", methods=["GET", "POST"])
def chat_unified():
    """Unified endpoint for Coze chat completions with proper streaming."""
    try:
        if request.method == "GET":
            # Handle SSE requests with query parameters
            message = request.args.get('message', '')
            file_id = request.args.get('file_id')
            user_id = request.args.get('user_id', 'default_user')
            bot_id = request.args.get('bot_id', COZE_BOT_ID)
        else:
            # Handle JSON POST request
            data = request.json or {}
            message = data.get('message', '')
            file_id = data.get('file_id')
            user_id = data.get('user_id', 'default_user')
            bot_id = data.get('bot_id', COZE_BOT_ID)

        # Initialize conversation if needed
        if user_id not in conversation_store:
            conversation_store[user_id] = {}

        if bot_id not in conversation_store[user_id]:
            initial_message = Message.build_user_question_text("You are an AI assistant. Let's begin our conversation.")
            conversation = coze.conversations.create(messages=[initial_message])
            conversation_store[user_id][bot_id] = conversation.id

        conversation_id = conversation_store[user_id][bot_id]

        def generate():
            try:
                yield f"data: {json.dumps({'type': 'start'})}\n\n"
                
                messages = []
                if file_id:
                    messages.append(
                        Message.build_user_question_objects([
                            MessageObjectString.build_text(message or "Please describe this image"),
                            MessageObjectString.build_image(file_id=file_id)
                        ])
                    )
                else:
                    messages.append(Message.build_user_question_text(message))

                total_tokens = 0
                for event in coze.chat.stream(
                    bot_id=bot_id,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    additional_messages=messages
                ):
                    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                        total_tokens += len(event.message.content.split())
                        yield f"data: {json.dumps({
                            'type': 'delta', 
                            'content': event.message.content,
                            'tokens': total_tokens
                        })}\n\n"
                    elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                        yield f"data: {json.dumps({
                            'type': 'complete',
                            'tokens': total_tokens
                        })}\n\n"

            except Exception as e:
                logger.error(f"Error in chat stream: {str(e)}\n{traceback.format_exc()}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return Response(
            stream_with_context(generate()),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5088) 