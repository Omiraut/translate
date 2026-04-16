#!/usr/bin/env python3
"""
Demo script for Translation API
Shows how to use the API with example requests
Run this script when the API is running: python demo.py
"""

import requests
import json
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

# Colors for terminal output
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_section(title):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.ENDC}\n")


def print_success(msg):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")


def print_info(msg):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {msg}{Colors.ENDC}")


def print_error(msg):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")


def print_request(method, endpoint, data=None):
    """Print request details"""
    print(f"{Colors.OKBLUE}{method} {endpoint}{Colors.ENDC}")
    if data:
        print(f"Request: {json.dumps(data, indent=2)}")


def print_response(response):
    """Print response details"""
    try:
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")


def test_health_check():
    """Test health check endpoint"""
    print_section("1. Health Check")
    print_request("GET", "/health")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response)
        
        if response.status_code == 200:
            print_success("Server is running ✓")
            return True
        else:
            print_error("Server health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Make sure it's running on http://localhost:8000")
        print_info("Run the API with: python main.py")
        return False


def test_list_languages():
    """Test list languages endpoint"""
    print_section("2. List Supported Languages")
    print_request("GET", "/languages")
    
    try:
        response = requests.get(f"{BASE_URL}/languages")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            languages = data["data"]
            print_success(f"Retrieved {len(languages)} supported languages")
        else:
            print_error("Failed to retrieve languages")
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_translations():
    """Test translation endpoints"""
    print_section("3. Translation Examples")
    
    # Test cases: (message, language_code, language_name)
    test_cases = [
        ("Hi", "hi", "Hindi"),
        ("Good morning", "mr", "Marathi"),
        ("Hello world", "gu", "Gujarati"),
        ("Thank you", "bn", "Bengali"),
        ("Welcome", "ta", "Tamil"),
        ("Good bye", "te", "Telugu"),
        ("Help", "kn", "Kannada"),
        ("Beautiful", "ml", "Malayalam"),
    ]

    for i, (message, lang_code, lang_name) in enumerate(test_cases, 1):
        print(f"\n{Colors.BOLD}3.{i} Translate to {lang_name} ({lang_code}){Colors.ENDC}")
        print_request("POST", "/translate", {"message": message, "language": lang_code})
        
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json={"message": message, "language": lang_code}
            )
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                converted = data["data"]["converted_text"]
                print_success(f"'{message}' → '{converted}'")
            else:
                print_error(f"Translation failed: {response.status_code}")
        except Exception as e:
            print_error(f"Error: {str(e)}")


def test_caching():
    """Test caching functionality"""
    print_section("4. Caching Test")
    
    message = "Hello"
    language = "hi"
    
    # First request
    print(f"{Colors.BOLD}First Request (should hit translation library):{Colors.ENDC}")
    print_request("POST", "/translate", {"message": message, "language": language})
    
    try:
        start = datetime.now()
        response1 = requests.post(
            f"{BASE_URL}/translate",
            json={"message": message, "language": language}
        )
        time1 = (datetime.now() - start).total_seconds()
        
        print_response(response1)
        if response1.status_code == 200:
            data1 = response1.json()
            print_success(f"Translation: '{data1['data']['converted_text']}' (Time: {time1:.3f}s)")
            print_info(f"Cached: {data1['data']['cached']}")
        
        # Second request (should be cached)
        print(f"\n{Colors.BOLD}Second Request (should be from cache):{Colors.ENDC}")
        print_request("POST", "/translate", {"message": message, "language": language})
        
        start = datetime.now()
        response2 = requests.post(
            f"{BASE_URL}/translate",
            json={"message": message, "language": language}
        )
        time2 = (datetime.now() - start).total_seconds()
        
        print_response(response2)
        if response2.status_code == 200:
            data2 = response2.json()
            print_success(f"Translation: '{data2['data']['converted_text']}' (Time: {time2:.3f}s)")
            print_info(f"Cached: {data2['data']['cached']}")
            
            if data2["data"]["cached"]:
                print_success(f"Cache hit! Response was {time1/time2:.1f}x faster")
            
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_error_handling():
    """Test error handling"""
    print_section("5. Error Handling Tests")
    
    test_cases = [
        ("Empty message", {"message": "", "language": "hi"}, "Should reject empty message"),
        ("Invalid language", {"message": "Hello", "language": "xyz"}, "Should reject invalid language"),
        ("Whitespace message", {"message": "   ", "language": "hi"}, "Should reject whitespace-only message"),
    ]
    
    for i, (description, payload, expectation) in enumerate(test_cases, 1):
        print(f"\n{Colors.BOLD}5.{i} {description}{Colors.ENDC}")
        print_info(expectation)
        print_request("POST", "/translate", payload)
        
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json=payload
            )
            print_response(response)
            
            if response.status_code != 200:
                print_success("Error correctly rejected with status code 400/422")
            else:
                print_error("Should have returned an error")
        except Exception as e:
            print_error(f"Error: {str(e)}")


def test_statistics():
    """Test statistics endpoint"""
    print_section("6. Service Statistics")
    print_request("GET", "/stats")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            stats = data["data"]
            print_success(f"Total translations: {stats['total_translations']}")
            print_success(f"Cached entries: {stats['cache_stats']['total_entries']}")
        else:
            print_error("Failed to retrieve stats")
    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_cache_clear():
    """Test cache clear endpoint"""
    print_section("7. Clear Cache")
    print_request("POST", "/cache/clear")
    
    try:
        response = requests.post(f"{BASE_URL}/cache/clear")
        print_response(response)
        
        if response.status_code == 200:
            print_success("Cache cleared successfully")
        else:
            print_error("Failed to clear cache")
    except Exception as e:
        print_error(f"Error: {str(e)}")


def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          Translation API - Full Demo & Test Suite        ║")
    print("║                                                            ║")
    print(f"║  Testing: {BASE_URL:<45}║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")
    
    # Test health first
    if not test_health_check():
        print_error("\n➜ Cannot connect to API. Please ensure it's running.")
        return
    
    # Run other tests
    test_list_languages()
    test_translations()
    test_caching()
    test_error_handling()
    test_statistics()
    test_cache_clear()
    
    # Final summary
    print_section("Demo Complete")
    print_success("All tests completed!")
    print_info("For interactive API documentation, visit:")
    print_info(f"  • Swagger UI: {BASE_URL}/docs")
    print_info(f"  • ReDoc: {BASE_URL}/redoc")
    print()


if __name__ == "__main__":
    main()
