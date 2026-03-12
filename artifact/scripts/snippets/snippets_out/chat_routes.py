from flask import Blueprint, request, jsonify, Response, stream_with_context
import requests
import json
import os
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('chat', __name__)

# Constants
OPENAI_API_URL = os.getenv('OPENAI_API_URL', 'https://api.openai.com/v1')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_URL = os.getenv('ANTHROPIC_API_URL', 'https://api.anthropic.com/v1')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Store for conversations
conversation_store = {}

@bp.before_request
def before_request():
    """Log incoming requests"""
    logger.info(f"Incoming request: {request.method} {request.path}")
    if request.is_json:
        logger.debug(f"Request data: {request.get_json()}")

@bp.route('/chat/completions', methods=['POST'])
def chat_completions():
    """
    Generic chat completions endpoint that can route to different LLM providers
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        # Extract request parameters
        provider = data.pop('provider', 'openai').lower()
        model = data.get('model', 'gpt-3.5-turbo')
        messages = data.get('messages', [])
        stream = data.get('stream', True)
        
        # Route to the appropriate provider
        if provider == 'openai':
            return openai_chat_completion(data, stream)
        elif provider == 'anthropic':
            return anthropic_chat_completion(data, stream)
        else:
            return jsonify({"error": f"Unsupported provider: {provider}"}), 400
            
    except Exception as e:
        logger.error(f"Error in chat completions: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

def openai_chat_completion(data, stream=True):
    """
    Forward chat completions to OpenAI compatible API
    """
    try:
        api_key = data.pop('api_key', OPENAI_API_KEY)
        if not api_key:
            return jsonify({"error": "OpenAI API key not configured"}), 401
            
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{OPENAI_API_URL}/chat/completions",
            json=data,
            headers=headers,
            stream=stream,
            timeout=60
        )
        
        if response.status_code != 200:
            return jsonify({"error": f"OpenAI API error: {response.text}"}), response.status_code
            
        # Handle streaming response
        if stream:
            def generate():
                for chunk in response.iter_lines():
                    if chunk:
                        chunk_text = chunk.decode('utf-8')
                        if chunk_text.startswith('data: '):
                            yield f"{chunk_text}\n"
                        else:
                            yield f"data: {chunk_text}\n\n"
                            
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
            return response.json()
            
    except Exception as e:
        logger.error(f"OpenAI chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def anthropic_chat_completion(data, stream=True):
    """
    Forward chat completions to Anthropic API
    """
    try:
        api_key = data.pop('api_key', ANTHROPIC_API_KEY)
        if not api_key:
            return jsonify({"error": "Anthropic API key not configured"}), 401
            
        # Convert OpenAI format to Anthropic format if needed
        if 'messages' in data:
            messages = data.pop('messages', [])
            system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
            
            # Build Anthropic-compatible request
            anthropic_data = {
                "model": data.get('model', 'claude-3-opus-20240229'),
                "max_tokens": data.get('max_tokens', 1024),
                "temperature": data.get('temperature', 0.7),
                "stream": stream,
                "messages": [m for m in messages if m['role'] != 'system']
            }
            
            if system_message:
                anthropic_data["system"] = system_message
                
            data = anthropic_data
            
        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{ANTHROPIC_API_URL}/messages",
            json=data,
            headers=headers,
            stream=stream,
            timeout=60
        )
        
        if response.status_code != 200:
            return jsonify({"error": f"Anthropic API error: {response.text}"}), response.status_code
            
        # Handle streaming response
        if stream:
            def generate():
                for chunk in response.iter_lines():
                    if chunk:
                        chunk_text = chunk.decode('utf-8')
                        if chunk_text.startswith('data: '):
                            # Already in SSE format
                            yield f"{chunk_text}\n"
                        else:
                            # Convert to SSE format
                            yield f"data: {chunk_text}\n\n"
                            
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
            return response.json()
            
    except Exception as e:
        logger.error(f"Anthropic chat error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/clear', methods=['POST'])
def clear_conversation():
    """
    Clear a chat conversation
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        provider = data.get('provider', 'openai')

        if user_id in conversation_store and provider in conversation_store[user_id]:
            del conversation_store[user_id][provider]
            return jsonify({'success': True}), 200
        return jsonify({'error': 'Conversation not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/models', methods=['GET'])
def list_models():
    """
    List available models from various providers
    """
    try:
        provider = request.args.get('provider', 'openai').lower()
        
        if provider == 'openai':
            if not OPENAI_API_KEY:
                return jsonify({"error": "OpenAI API key not configured"}), 401
                
            headers = {
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{OPENAI_API_URL}/models",
                headers=headers
            )
            
            if response.status_code != 200:
                return jsonify({"error": f"OpenAI API error: {response.text}"}), response.status_code
                
            return response.json()
            
        elif provider == 'anthropic':
            # Anthropic doesn't have a models endpoint, so we'll return a static list
            return jsonify({
                "object": "list",
                "data": [
                    {"id": "claude-3-opus-20240229", "object": "model"},
                    {"id": "claude-3-sonnet-20240229", "object": "model"},
                    {"id": "claude-3-haiku-20240307", "object": "model"},
                    {"id": "claude-2.1", "object": "model"},
                    {"id": "claude-2.0", "object": "model"},
                    {"id": "claude-instant-1.2", "object": "model"}
                ]
            })
            
        else:
            return jsonify({"error": f"Unsupported provider: {provider}"}), 400
            
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return jsonify({"error": str(e)}), 500 