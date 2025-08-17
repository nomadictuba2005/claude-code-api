#!/usr/bin/env python3
"""
Test script for Claude Code API
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_models():
    """Test models endpoint"""
    print("Testing /v1/models endpoint...")
    response = requests.get(f"{API_BASE}/v1/models")
    print(f"Status: {response.status_code}")
    print(f"Available models: {[model['id'] for model in response.json()['data']]}")
    print()

def test_chat_completion():
    """Test chat completion endpoint"""
    print("Testing /v1/chat/completions endpoint...")
    
    payload = {
        "model": "claude-sonnet-4",
        "messages": [
            {"role": "user", "content": "Say hello and tell me what 2+2 equals"}
        ]
    }
    
    response = requests.post(
        f"{API_BASE}/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Claude's response: {result['choices'][0]['message']['content']}")
        print(f"Token usage: {result['usage']}")
    else:
        print(f"Error: {response.text}")
    print()

def test_different_models():
    """Test different Claude models"""
    models_to_test = ["claude-sonnet-4", "claude-haiku-3.5"]
    
    for model in models_to_test:
        print(f"Testing model: {model}")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hi! Just respond with 'Hello from [model name]'"}
            ]
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ {model}: {result['choices'][0]['message']['content']}")
            else:
                print(f"✗ {model}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"✗ {model}: {str(e)}")
    
    print()

def test_with_openai_library():
    """Test using the openai library"""
    try:
        import openai
        
        print("Testing with OpenAI library...")
        
        client = openai.OpenAI(
            api_key="not-needed",
            base_url=f"{API_BASE}/v1"
        )
        
        response = client.chat.completions.create(
            model="claude-sonnet-4",
            messages=[
                {"role": "user", "content": "Write a short Python function to add two numbers"}
            ]
        )
        
        print(f"OpenAI library response:")
        print(f"Content: {response.choices[0].message.content}")
        print()
        
    except ImportError:
        print("OpenAI library not installed. Install with: pip install openai")
        print()

if __name__ == "__main__":
    print("Claude Code API Test Suite")
    print("=" * 40)
    print()
    
    try:
        test_health()
        test_models()
        test_chat_completion()
        test_different_models()
        test_with_openai_library()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"Error during testing: {e}")