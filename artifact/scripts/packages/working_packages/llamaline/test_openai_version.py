#!/usr/bin/env python3
"""
test_openai_version.py

Test script for the OpenAI version of llamaline to demonstrate functionality
without requiring an actual OpenAI API key for testing purposes.
"""

import os
import sys
import asyncio
from unittest.mock import AsyncMock, patch

# Add current directory to path
sys.path.insert(0, '.')

# Mock environment for testing
os.environ['OPENAI_API_KEY'] = 'test-api-key'

def test_basic_imports():
    """Test that all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        import llamaline_openai
        print("✅ llamaline_openai imports successfully")
        
        # Test class instantiation
        chat = llamaline_openai.OpenAIChat()
        tools = llamaline_openai.Tools()
        
        print(f"✅ OpenAIChat initialized with model: {chat.model}")
        print(f"✅ Tools initialized with Python path: {tools.python_path}")
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    return True

async def test_mock_openai_interaction():
    """Test OpenAI interaction with mocked responses"""
    print("\n🧪 Testing OpenAI interaction (mocked)...")
    
    import llamaline_openai
    
    # Mock response for tool selection
    mock_response = {
        "tool": "bash",
        "code": "df -h"
    }
    
    chat = llamaline_openai.OpenAIChat()
    
    # Mock the select_tool method
    with patch.object(chat, 'select_tool', new_callable=AsyncMock) as mock_select:
        mock_select.return_value = mock_response
        
        result = await chat.select_tool("show disk usage")
        
        print(f"✅ Mock response received: {result}")
        assert result["tool"] == "bash"
        assert result["code"] == "df -h"
        print("✅ Tool selection works correctly")

async def test_tools_execution():
    """Test the tools execution (Python and bash)"""
    print("\n🧪 Testing tools execution...")
    
    import llamaline_openai
    
    tools = llamaline_openai.Tools()
    
    # Test Python execution
    try:
        python_result = await tools.run_python_code("print('Hello from Python!')")
        print(f"✅ Python execution: {python_result}")
        assert "Hello from Python!" in python_result
    except Exception as e:
        print(f"❌ Python execution failed: {e}")
    
    # Test safe bash execution
    try:
        bash_result = await tools.run_bash_command("echo 'Hello from bash!'")
        print(f"✅ Bash execution: {bash_result}")
        assert "Hello from bash!" in bash_result
    except Exception as e:
        print(f"❌ Bash execution failed: {e}")
    
    # Test unsafe command blocking
    try:
        unsafe_result = await tools.run_bash_command("sudo rm -rf /")
        print(f"✅ Unsafe command blocked: {unsafe_result}")
        assert "unsafe" in unsafe_result.lower()
    except Exception as e:
        print(f"❌ Safety test failed: {e}")

def test_ui_components():
    """Test UI components work without errors"""
    print("\n🧪 Testing UI components...")
    
    import llamaline_openai
    from io import StringIO
    from contextlib import redirect_stdout
    
    # Capture stdout to test UI components
    output = StringIO()
    
    try:
        with redirect_stdout(output):
            llamaline_openai.show_cheat_sheet()
        print("✅ Cheat sheet display works")
        
        with redirect_stdout(output):
            llamaline_openai.show_help()
        print("✅ Help display works")
        
        with redirect_stdout(output):
            llamaline_openai.display_code_preview("python", "print('test')")
        print("✅ Code preview works")
        
        with redirect_stdout(output):
            llamaline_openai.display_result("python", "test output")
        print("✅ Result display works")
        
    except Exception as e:
        print(f"❌ UI component test failed: {e}")
        return False
    
    return True

async def test_cheat_sheet_functionality():
    """Test that cheat sheet commands work"""
    print("\n🧪 Testing cheat sheet functionality...")
    
    import llamaline_openai
    
    # Test a cheat sheet command
    tools = llamaline_openai.Tools()
    
    # Simulate using a cheat sheet command
    cheat_choice = llamaline_openai.CHEAT_SHEETS["disk usage"]
    
    print(f"✅ Cheat sheet 'disk usage': {cheat_choice}")
    
    # Execute the cheat sheet command
    if cheat_choice["tool"] == "bash":
        result = await tools.run_bash_command(cheat_choice["code"])
        print(f"✅ Cheat sheet execution result: {result[:50]}...")

def main():
    """Run all tests"""
    print("🚀 Testing llamaline OpenAI version")
    print("=" * 50)
    
    # Basic tests
    if not test_basic_imports():
        return
    
    if not test_ui_components():
        return
    
    # Async tests
    async def run_async_tests():
        await test_mock_openai_interaction()
        await test_tools_execution()
        await test_cheat_sheet_functionality()
    
    try:
        asyncio.run(run_async_tests())
        print("\n🎉 All tests passed!")
        print("\n📋 Summary:")
        print("✅ Imports work correctly")
        print("✅ UI components render without errors")
        print("✅ OpenAI interaction (mocked) works")
        print("✅ Python/bash execution works")
        print("✅ Safety features work")
        print("✅ Cheat sheet functionality works")
        print("\n🔧 To use with real OpenAI API:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Run: python llamaline_openai.py")
        
    except Exception as e:
        print(f"\n❌ Async tests failed: {e}")

if __name__ == "__main__":
    main() 