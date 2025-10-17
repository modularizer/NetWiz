#!/usr/bin/env python3
"""
Health check script for NetWiz Backend API

This script checks the health of the running API service and provides
detailed status information.

Usage:
    netwiz-health                    # Check health with default settings
    netwiz-health --url http://localhost:5000
    netwiz-health --timeout 10
    netwiz-health --verbose
"""

import argparse
import sys
from datetime import datetime

import requests


def check_health(
    base_url: str = "http://localhost:5000", timeout: int = 5, verbose: bool = False
) -> bool:
    """
    Check the health of the NetWiz Backend API

    Args:
        base_url: Base URL of the API
        timeout: Request timeout in seconds
        verbose: Whether to show detailed output

    Returns:
        True if healthy, False otherwise
    """
    try:
        # Check health endpoint
        health_url = f"{base_url}/health"
        if verbose:
            print(f"🔍 Checking health at: {health_url}")

        response = requests.get(health_url, timeout=timeout)

        if response.status_code == 200:
            health_data = response.json()

            if verbose:
                print("✅ API is healthy!")
                print(f"   Status: {health_data.get('status', 'unknown')}")
                print(f"   Version: {health_data.get('version', 'unknown')}")
                print(f"   Environment: {health_data.get('environment', 'unknown')}")
                print(f"   Timestamp: {health_data.get('timestamp', 'unknown')}")
            else:
                print("✅ API is healthy")

            return True
        else:
            if verbose:
                print(f"❌ API returned status code: {response.status_code}")
                print(f"   Response: {response.text}")
            else:
                print("❌ API is unhealthy")

            return False

    except requests.exceptions.ConnectionError:
        if verbose:
            print(f"❌ Cannot connect to API at {base_url}")
            print("   Make sure the API server is running")
        else:
            print("❌ Cannot connect to API")
        return False

    except requests.exceptions.Timeout:
        if verbose:
            print(f"❌ Request timed out after {timeout} seconds")
        else:
            print("❌ Request timed out")
        return False

    except Exception as e:
        if verbose:
            print(f"❌ Unexpected error: {e}")
        else:
            print("❌ Health check failed")
        return False


def check_openapi(base_url: str = "http://localhost:5000", timeout: int = 5) -> bool:
    """
    Check if OpenAPI schema is accessible

    Args:
        base_url: Base URL of the API
        timeout: Request timeout in seconds

    Returns:
        True if accessible, False otherwise
    """
    try:
        openapi_url = f"{base_url}/openapi.json"
        response = requests.get(openapi_url, timeout=timeout)

        if response.status_code == 200:
            schema = response.json()
            print(
                f"📚 OpenAPI schema accessible ({len(schema.get('paths', {}))} endpoints)"
            )
            return True
        else:
            print(f"❌ OpenAPI schema not accessible (status: {response.status_code})")
            return False

    except Exception as e:
        print(f"❌ Cannot access OpenAPI schema: {e}")
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Check the health of NetWiz Backend API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  netwiz-health                           # Basic health check
  netwiz-health --url http://localhost:8000  # Check different URL
  netwiz-health --timeout 10 --verbose    # Detailed output with longer timeout
  netwiz-health --openapi                 # Also check OpenAPI schema
        """,
    )

    parser.add_argument(
        "--url",
        default="http://localhost:5000",
        help="Base URL of the API (default: http://localhost:5000)",
    )

    parser.add_argument(
        "--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )

    parser.add_argument(
        "--openapi", action="store_true", help="Also check OpenAPI schema accessibility"
    )

    args = parser.parse_args()

    print("🏥 NetWiz Backend Health Check")
    print(f"   URL: {args.url}")
    print(f"   Timeout: {args.timeout}s")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print()

    # Check health
    health_ok = check_health(args.url, args.timeout, args.verbose)

    # Check OpenAPI if requested
    openapi_ok = True
    if args.openapi:
        print()
        openapi_ok = check_openapi(args.url, args.timeout)

    # Overall status
    print()
    if health_ok and openapi_ok:
        print("🎉 All checks passed!")
        sys.exit(0)
    else:
        print("💥 Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
