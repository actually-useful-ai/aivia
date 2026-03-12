"""
Unified Test Configuration and Fixtures
=======================================

Central configuration for all AI development ecosystem tests.
Provides shared fixtures, utilities, and test setup for all platforms.

Platforms covered:
- Beltalowda Multi-Agent Orchestration
- Swarm Tool Ecosystem
- Enterprise Orchestration
- xAI Swarm Integration
"""

import os
import sys
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test configuration
TEST_CONFIG = {
    'project_root': PROJECT_ROOT,
    'test_data_dir': Path(__file__).parent / 'fixtures',
    'temp_dir': None,  # Set in session fixture
    'mock_api_keys': {
        'XAI_API_KEY': 'test-xai-key-12345',
        'OPENAI_API_KEY': 'test-openai-key-12345',
        'ANTHROPIC_API_KEY': 'test-anthropic-key-12345',
        'MISTRAL_API_KEY': 'test-mistral-key-12345',
        'COHERE_API_KEY': 'test-cohere-key-12345',
        'GOOGLE_API_KEY': 'test-google-key-12345',
        'SERPAPI_API_KEY': 'test-serpapi-key-12345',
        'TAVILY_API_KEY': 'test-tavily-key-12345',
        'NYT_API_KEY': 'test-nyt-key-12345',
    },
    'test_endpoints': {
        'beltalowda_api': 'http://localhost:8000',
        'swarm_api': 'http://localhost:5001',
        'enterprise_api': 'http://localhost:8080',
        'xai_api': 'https://api.x.ai/v1',
        'openai_api': 'https://api.openai.com/v1',
        'anthropic_api': 'https://api.anthropic.com/v1',
    }
}

# ============================================================================
# SESSION FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Global test configuration"""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def temp_dir():
    """Session-wide temporary directory"""
    temp_path = tempfile.mkdtemp(prefix="ai_ecosystem_test_")
    TEST_CONFIG['temp_dir'] = Path(temp_path)
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture(scope="session")
def event_loop():
    """Session-wide event loop for async tests"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

# ============================================================================
# ENVIRONMENT FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    """Automatically mock environment variables for all tests"""
    # Set mock API keys
    for key, value in TEST_CONFIG['mock_api_keys'].items():
        monkeypatch.setenv(key, value)

    # Set test mode flags
    monkeypatch.setenv('TESTING', 'true')
    monkeypatch.setenv('DEBUG', 'false')
    monkeypatch.setenv('LOG_LEVEL', 'INFO')

    # Disable external API calls by default
    monkeypatch.setenv('DISABLE_EXTERNAL_APIS', 'true')

    return TEST_CONFIG['mock_api_keys']

@pytest.fixture
def real_environment(monkeypatch):
    """Enable real API calls for integration tests (use sparingly)"""
    monkeypatch.setenv('DISABLE_EXTERNAL_APIS', 'false')
    # Remove mock keys to force real ones
    for key in TEST_CONFIG['mock_api_keys'].keys():
        monkeypatch.delenv(key, raising=False)

# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    client = Mock()
    client.chat = Mock()
    client.chat.completions = Mock()
    client.chat.completions.create = AsyncMock()
    client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Test response from OpenAI"))]
    )
    return client

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client"""
    client = Mock()
    client.messages = Mock()
    client.messages.create = AsyncMock()
    client.messages.create.return_value = Mock(
        content=[Mock(text="Test response from Anthropic")]
    )
    return client

@pytest.fixture
def mock_xai_client():
    """Mock xAI/Grok client"""
    client = Mock()
    client.chat = Mock()
    client.chat.completions = Mock()
    client.chat.completions.create = AsyncMock()
    client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Test response from xAI Grok"))]
    )
    return client

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for API calls"""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client

# ============================================================================
# PLATFORM-SPECIFIC FIXTURES
# ============================================================================

@pytest.fixture
def beltalowda_config():
    """Beltalowda platform test configuration"""
    return {
        'agent_hierarchy': ['belter', 'drummer', 'camina'],
        'test_task': {
            'type': 'research',
            'query': 'Test research query',
            'depth': 'basic'
        },
        'mock_responses': {
            'belter': "Belter agent response",
            'drummer': "Drummer agent response",
            'camina': "Camina agent response"
        }
    }

@pytest.fixture
def swarm_config():
    """Swarm platform test configuration"""
    return {
        'modules': ['search', 'research', 'finance', 'news'],
        'test_query': 'Test swarm query',
        'mock_search_results': [
            {'title': 'Test Result 1', 'url': 'https://example.com/1'},
            {'title': 'Test Result 2', 'url': 'https://example.com/2'}
        ]
    }

@pytest.fixture
def enterprise_config():
    """Enterprise orchestration test configuration"""
    return {
        'workflows': ['data_analysis', 'report_generation'],
        'test_workflow': {
            'name': 'test_analysis',
            'steps': ['collect', 'process', 'analyze', 'report']
        },
        'monitoring': {
            'metrics': ['response_time', 'success_rate', 'error_count'],
            'alerts': ['high_error_rate', 'slow_response']
        }
    }

# ============================================================================
# DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_user_message():
    """Sample user message for testing"""
    return {
        'role': 'user',
        'content': 'This is a test message for the AI assistant.'
    }

@pytest.fixture
def sample_conversation():
    """Sample conversation history"""
    return [
        {'role': 'user', 'content': 'Hello, can you help me?'},
        {'role': 'assistant', 'content': 'Hello! I\'d be happy to help. What do you need assistance with?'},
        {'role': 'user', 'content': 'I need information about AI development.'}
    ]

@pytest.fixture
def sample_search_query():
    """Sample search query"""
    return {
        'query': 'artificial intelligence development best practices',
        'filters': ['academic', 'recent'],
        'max_results': 10
    }

@pytest.fixture
def sample_task_request():
    """Sample task request"""
    return {
        'task_id': 'test-task-123',
        'task_type': 'research',
        'parameters': {
            'query': 'machine learning trends 2025',
            'depth': 'comprehensive',
            'sources': ['academic', 'industry', 'news']
        },
        'priority': 'normal',
        'timeout': 300
    }

# ============================================================================
# UTILITY FIXTURES
# ============================================================================

@pytest.fixture
def temp_file(temp_dir):
    """Create a temporary file for testing"""
    def _create_temp_file(content="", suffix=".txt"):
        temp_file_path = temp_dir / f"test_file_{os.getpid()}{suffix}"
        temp_file_path.write_text(content)
        return temp_file_path
    return _create_temp_file

@pytest.fixture
def mock_file_system(monkeypatch, temp_dir):
    """Mock file system operations"""
    original_open = open

    def mock_open(file, mode='r', **kwargs):
        if isinstance(file, str) and file.startswith('/mock/'):
            # Redirect mock paths to temp directory
            mock_path = temp_dir / file.replace('/mock/', '')
            mock_path.parent.mkdir(parents=True, exist_ok=True)
            return original_open(mock_path, mode, **kwargs)
        return original_open(file, mode, **kwargs)

    monkeypatch.setattr('builtins.open', mock_open)
    return temp_dir

# ============================================================================
# SKIP CONDITIONS
# ============================================================================

def skip_if_no_api_key(provider: str):
    """Skip test if real API key is not available"""
    key_name = f"{provider.upper()}_API_KEY"
    real_key = os.getenv(key_name)
    mock_key = TEST_CONFIG['mock_api_keys'].get(key_name)

    return pytest.mark.skipif(
        not real_key or real_key == mock_key,
        reason=f"Real {provider} API key not available"
    )

def skip_if_no_internet():
    """Skip test if internet connection is not available"""
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return pytest.mark.skipif(False, reason="")
    except OSError:
        return pytest.mark.skipif(True, reason="No internet connection")

# ============================================================================
# PYTEST HOOKS
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Add custom markers
    for marker_name, marker_description in [
        ("unit", "Unit tests for individual components"),
        ("integration", "Integration tests across components"),
        ("e2e", "End-to-end tests for complete workflows"),
        ("slow", "Tests that take more than 5 seconds"),
        ("api", "Tests requiring external API calls"),
        ("accessibility", "Accessibility compliance tests"),
        ("security", "Security and authentication tests"),
        ("performance", "Performance and load tests"),
    ]:
        config.addinivalue_line("markers", f"{marker_name}: {marker_description}")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers"""
    for item in items:
        # Add slow marker to tests that might be slow
        if any(keyword in item.name.lower() for keyword in ['integration', 'e2e', 'api', 'external']):
            item.add_marker(pytest.mark.slow)

        # Add api marker to tests that use external APIs
        if any(keyword in item.name.lower() for keyword in ['api', 'openai', 'anthropic', 'xai', 'external']):
            item.add_marker(pytest.mark.api)

def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    print("\n" + "="*80)
    print("AI Development Ecosystem Test Suite")
    print("="*80)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Test Data Directory: {TEST_CONFIG['test_data_dir']}")
    print(f"Mock API Keys: {len(TEST_CONFIG['mock_api_keys'])} configured")
    print("="*80 + "\n")

def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    print("\n" + "="*80)
    print("Test Session Complete")
    print(f"Exit Status: {exitstatus}")
    print("="*80 + "\n")