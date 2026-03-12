"""Pytest configuration for namecrawler tests"""

import pytest


@pytest.fixture
def sample_content():
    """Provide sample content for testing"""
    return b"Sample file content for testing"

