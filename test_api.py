#!/usr/bin/env python
"""
Script to test all API endpoints and verify they return correct results
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_endpoint(method, url, description, data=None, params=None):
    """Test an API endpoint"""
    print(f"\n[TEST] {description}")
    print(f"  {method} {url}")
    
    try:
        if method == 'GET':
            response = requests.get(url, params=params, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, params=params, timeout=5)
        else:
            print(f"  [ERROR] Unsupported method: {method}")
            return False
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                result = response.json()
                print(f"  [SUCCESS] Response received")
                if isinstance(result, dict):
                    # Show key information
                    if 'count' in result:
                        print(f"  Count: {result['count']}")
                    if 'results' in result:
                        print(f"  Results: {len(result['results'])} items")
                    if 'message' in result:
                        print(f"  Message: {result['message']}")
                elif isinstance(result, list):
                    print(f"  Items: {len(result)}")
                return True
            except json.JSONDecodeError:
                print(f"  [WARNING] Response is not JSON")
                print(f"  Response: {response.text[:200]}")
                return False
        else:
            print(f"  [ERROR] Request failed")
            try:
                error = response.json()
                print(f"  Error: {error}")
            except:
                print(f"  Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] Could not connect to server. Is it running?")
        return False
    except requests.exceptions.Timeout:
        print(f"  [ERROR] Request timed out")
        return False
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

def main():
    print_section("API ENDPOINT TESTING")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test Dashboard Stats
    print_section("Dashboard Statistics")
    results.append(("Dashboard Stats", test_endpoint(
        'GET', f"{BASE_URL}/api/dashboard/stats/",
        "Get dashboard statistics"
    )))
    
    # Test Competitors
    print_section("Competitors API")
    results.append(("Competitors List", test_endpoint(
        'GET', f"{BASE_URL}/api/competitors/",
        "Get all competitors"
    )))
    results.append(("Competitors (Active Only)", test_endpoint(
        'GET', f"{BASE_URL}/api/competitors/",
        "Get active competitors only",
        params={'is_active': 'true'}
    )))
    
    # Test Updates
    print_section("Updates API")
    results.append(("Updates List", test_endpoint(
        'GET', f"{BASE_URL}/api/updates/",
        "Get all updates"
    )))
    results.append(("Updates (High Impact)", test_endpoint(
        'GET', f"{BASE_URL}/api/updates/",
        "Get high impact updates only",
        params={'high_impact': 'true'}
    )))
    results.append(("Updates (Last 7 Days)", test_endpoint(
        'GET', f"{BASE_URL}/api/updates/",
        "Get updates from last 7 days",
        params={'days': '7'}
    )))
    
    # Test Trends
    print_section("Trends API")
    results.append(("Trends List", test_endpoint(
        'GET', f"{BASE_URL}/api/trends/",
        "Get all trends"
    )))
    
    # Test Monitoring
    print_section("Monitoring API")
    results.append(("Run Monitoring", test_endpoint(
        'POST', f"{BASE_URL}/api/monitor/run/",
        "Trigger competitor monitoring"
    )))
    
    # Test API Root
    print_section("API Root")
    results.append(("API Root", test_endpoint(
        'GET', f"{BASE_URL}/api/",
        "Get API root"
    )))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    print("\nDetailed Results:")
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {status}: {name}")
    
    if passed == total:
        print("\n[SUCCESS] All API endpoints are working correctly!")
    else:
        print("\n[WARNING] Some endpoints failed. Check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        exit(1)

