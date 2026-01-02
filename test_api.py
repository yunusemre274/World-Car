"""
Test Client for FastAPI Routing API

Simple script to test the routing API endpoints.

Usage:
    1. Start the API: uvicorn main:app --reload
    2. Run this script: python test_api.py
"""

import requests
import json
from typing import Dict, Any


# API base URL
BASE_URL = "http://localhost:8000"


def print_response(title: str, response: requests.Response):
    """Pretty print API response."""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70)
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2))
    print("=" * 70)


def test_root():
    """Test root endpoint."""
    response = requests.get(f"{BASE_URL}/")
    print_response("GET / - API Information", response)
    return response.json()


def test_health():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print_response("GET /health - Health Check", response)
    return response.json()


def test_stats():
    """Test statistics endpoint."""
    response = requests.get(f"{BASE_URL}/stats")
    print_response("GET /stats - Network Statistics", response)
    return response.json()


def test_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, description: str = ""):
    """Test route computation."""
    params = {
        "start_lat": start_lat,
        "start_lon": start_lon,
        "end_lat": end_lat,
        "end_lon": end_lon
    }

    response = requests.get(f"{BASE_URL}/route", params=params)

    title = f"GET /route - {description}" if description else "GET /route"
    print_response(title, response)

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"\n✓ Route found!")
            print(f"  Distance: {data['total_distance']:.2f} meters ({data['total_distance']/1000:.2f} km)")
            print(f"  Nodes: {data['node_count']}")
            print(f"  First 5 nodes: {data['path'][:5]}")
        else:
            print(f"\n✗ No route found: {data.get('message')}")

    return response.json()


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("FastAPI Routing API - Test Client".center(70))
    print("=" * 70)
    print("\nTesting API endpoints...")

    try:
        # Test 1: API Information
        print("\n[1/5] Testing API Information Endpoint...")
        test_root()

        # Test 2: Health Check
        print("\n[2/5] Testing Health Check Endpoint...")
        health = test_health()

        if health.get('status') != 'healthy':
            print("\n✗ API is not healthy. Exiting tests.")
            return

        # Test 3: Statistics
        print("\n[3/5] Testing Statistics Endpoint...")
        test_stats()

        # Test 4: Valid Route (Moda to Fenerbahçe)
        print("\n[4/5] Testing Valid Route Computation...")
        test_route(
            start_lat=40.9856,
            start_lon=29.0298,
            end_lat=40.9638,
            end_lon=29.0408,
            description="Moda to Fenerbahçe"
        )

        # Test 5: Another Route (Kadıköy Square to Bağdat Avenue)
        print("\n[5/5] Testing Another Route...")
        test_route(
            start_lat=40.9904,
            start_lon=29.0255,
            end_lat=40.9780,
            end_lon=29.0450,
            description="Kadıköy Square to Bağdat Ave"
        )

        # Test 6: Invalid Coordinates (should fail)
        print("\n[BONUS] Testing Invalid Coordinates...")
        params = {
            "start_lat": 91.0,  # Invalid latitude
            "start_lon": 29.0298,
            "end_lat": 40.9638,
            "end_lon": 29.0408
        }
        response = requests.get(f"{BASE_URL}/route", params=params)
        print_response("GET /route - Invalid Latitude (Expected Error)", response)

        print("\n" + "=" * 70)
        print("✓ ALL TESTS COMPLETED".center(70))
        print("=" * 70 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 70)
        print("✗ ERROR: Cannot connect to API".center(70))
        print("=" * 70)
        print("\nMake sure the API is running:")
        print("  uvicorn main:app --reload")
        print(f"\nAPI should be available at: {BASE_URL}")
        print()

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
