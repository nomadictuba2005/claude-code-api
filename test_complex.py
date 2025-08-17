#!/usr/bin/env python3
"""
Complex test script for Claude Code API - tests all models with challenging tasks
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def print_separator(title):
    """Print a nice separator for test sections"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_model_with_task(model, task_description, prompt):
    """Test a specific model with a complex task"""
    print(f"\n🧪 Testing {model}")
    print(f"📝 Task: {task_description}")
    print("-" * 40)
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=120  # 2 minute timeout for complex tasks
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            usage = result['usage']
            
            print(f"✅ SUCCESS ({end_time - start_time:.1f}s)")
            print(f"📊 Tokens: {usage['total_tokens']} (prompt: {usage['prompt_tokens']}, completion: {usage['completion_tokens']})")
            print(f"💬 Response preview: {content[:200]}...")
            if len(content) > 200:
                print(f"📏 Full response length: {len(content)} characters")
            
            return True, content
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False, None
            
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT - Model took longer than 2 minutes")
        return False, None
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        return False, None

def test_all_models():
    """Test all models with various complex tasks"""
    
    print_separator("CLAUDE CODE API COMPLEX TESTING SUITE")
    
    # Test tasks for different models
    test_cases = [
        {
            "model": "claude-sonnet-4",
            "task": "Advanced Python Class Design",
            "prompt": "Write a Python class that implements a thread-safe task queue with methods to add tasks, process them in order, handle errors gracefully, and include proper logging. Add unit tests for the class."
        },
        {
            "model": "claude-opus-4", 
            "task": "Algorithm Explanation & Implementation",
            "prompt": "Explain the A* pathfinding algorithm and implement it in Python with a visual example showing how it finds the shortest path in a grid with obstacles."
        },
        {
            "model": "claude-haiku-3.5",
            "task": "Quick Code Review",
            "prompt": "Review this code and suggest improvements: def calc(x,y): return x+y if x>0 else y-x"
        },
        {
            "model": "claude-sonnet-3.7",
            "task": "API Design & Documentation", 
            "prompt": "Design a RESTful API for a library management system. Include endpoint definitions, request/response examples, error handling, and OpenAPI/Swagger documentation."
        },
        {
            "model": "claude-opus-4.1",
            "task": "System Architecture Analysis",
            "prompt": "Design a scalable microservices architecture for an e-commerce platform handling 1M+ users. Include database design, caching strategy, and deployment considerations."
        }
    ]
    
    results = []
    successful_tests = 0
    
    for test_case in test_cases:
        success, response = test_model_with_task(
            test_case["model"], 
            test_case["task"], 
            test_case["prompt"]
        )
        
        results.append({
            "model": test_case["model"],
            "task": test_case["task"], 
            "success": success,
            "response_length": len(response) if response else 0
        })
        
        if success:
            successful_tests += 1
            
        # Small delay between requests to be nice to the API
        time.sleep(2)
    
    # Summary
    print_separator("TEST RESULTS SUMMARY")
    print(f"✅ Successful tests: {successful_tests}/{len(test_cases)}")
    print(f"📊 Success rate: {(successful_tests/len(test_cases)*100):.1f}%")
    
    print("\n📋 Detailed Results:")
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        length = f"({result['response_length']} chars)" if result["success"] else ""
        print(f"  {status} {result['model']} - {result['task']} {length}")
    
    if successful_tests == len(test_cases):
        print("\n🎉 ALL TESTS PASSED! Your Claude Code API is working perfectly!")
    else:
        print(f"\n⚠️  {len(test_cases) - successful_tests} tests failed. Check the errors above.")

def test_api_health():
    """Quick health check before running complex tests"""
    print_separator("API HEALTH CHECK")
    
    try:
        # Test health endpoint
        health_response = requests.get(f"{API_BASE}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Health endpoint: OK")
        else:
            print(f"❌ Health endpoint failed: {health_response.status_code}")
            return False
            
        # Test models endpoint  
        models_response = requests.get(f"{API_BASE}/v1/models", timeout=10)
        if models_response.status_code == 200:
            models = models_response.json()
            model_count = len(models['data'])
            print(f"✅ Models endpoint: OK ({model_count} models available)")
            
            # List available models
            model_names = [model['id'] for model in models['data']]
            print(f"📋 Available models: {', '.join(model_names)}")
        else:
            print(f"❌ Models endpoint failed: {models_response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"💥 Health check failed: {e}")
        return False

def test_simple_request():
    """Test a simple request to ensure basic functionality"""
    print_separator("BASIC FUNCTIONALITY TEST")
    
    simple_test = {
        "model": "claude-sonnet-4",
        "task": "Basic Math",
        "prompt": "What is 15 * 23? Explain your calculation."
    }
    
    success, response = test_model_with_task(
        simple_test["model"],
        simple_test["task"], 
        simple_test["prompt"]
    )
    
    return success

if __name__ == "__main__":
    print("🚀 Claude Code API Complex Testing Suite")
    print("📡 Testing API at:", API_BASE)
    print("⏰ This may take several minutes to complete...")
    
    # Step 1: Health check
    if not test_api_health():
        print("\n❌ API health check failed. Make sure the server is running:")
        print("   python main.py")
        exit(1)
    
    # Step 2: Basic functionality test
    if not test_simple_request():
        print("\n❌ Basic functionality test failed. Check API configuration.")
        exit(1)
    
    # Step 3: Complex model testing
    test_all_models()
    
    print("\n🏁 Testing complete!")
    print("💡 Tip: Check the full responses in the output above to verify quality.")