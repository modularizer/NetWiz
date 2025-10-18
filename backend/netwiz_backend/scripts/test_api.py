#!/usr/bin/env python3
"""
Test API script for NetWiz Backend

This script provides comprehensive testing of the NetWiz Backend API
including all endpoints and functionality.

Usage:
    netwiz-test-api                    # Run all tests
    netwiz-test-api --endpoint health  # Test specific endpoint
    netwiz-test-api --url http://localhost:5000
    netwiz-test-api --verbose
"""

import argparse
import sys
from datetime import datetime
from typing import Any

import requests


class APITester:
    """Test suite for NetWiz Backend API"""

    def __init__(self, base_url: str = "http://localhost:5000", verbose: bool = False):
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "User-Agent": "NetWiz-API-Tester/1.0"}
        )

    def log(self, message: str, level: str = "INFO"):
        """Log a message with optional verbose output"""
        if self.verbose or level in ["ERROR", "SUCCESS"]:
            prefix = {
                "INFO": "i ",
                "SUCCESS": "✅",
                "ERROR": "❌",
                "WARNING": "⚠️ ",
            }.get(level, "📝")
            print(f"{prefix} {message}")

    def test_endpoint(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"
        self.log(f"Testing {method.upper()} {path}")

        try:
            response = self.session.request(method, url, **kwargs)

            result = {
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "success": 200 <= response.status_code < 300,
                "response_time": response.elapsed.total_seconds(),
                "url": url,
            }

            if self.verbose:
                result["headers"] = dict(response.headers)
                try:
                    result["json"] = response.json()
                except Exception:
                    result["text"] = response.text

            if result["success"]:
                self.log(
                    f"  Status: {response.status_code} ({result['response_time']:.3f}s)",
                    "SUCCESS",
                )
            else:
                self.log(
                    f"  Status: {response.status_code} - {response.text[:100]}", "ERROR"
                )

            return result

        except Exception as e:
            self.log(f"  Error: {e}", "ERROR")
            return {
                "method": method,
                "path": path,
                "success": False,
                "error": str(e),
                "url": url,
            }

    def test_health_endpoints(self) -> dict[str, Any]:
        """Test health and system endpoints"""
        self.log("🏥 Testing Health Endpoints")

        results = {}

        # Root endpoint
        results["root"] = self.test_endpoint("GET", "/")

        # Health endpoint
        results["health"] = self.test_endpoint("GET", "/health")

        # Info endpoint
        results["info"] = self.test_endpoint("GET", "/info")

        # OpenAPI schema
        results["openapi"] = self.test_endpoint("GET", "/openapi.json")

        return results

    def test_netlist_endpoints(self) -> dict[str, Any]:
        """Test netlist endpoints"""
        self.log("📋 Testing Netlist Endpoints")

        results = {}

        # List netlists
        results["list"] = self.test_endpoint("GET", "/netlist")

        # Validate netlist (with sample data)
        sample_netlist = {
            "netlist": {
                "components": [
                    {
                        "id": "U1",
                        "type": "IC",
                        "pins": [
                            {"number": "1", "name": "VCC"},
                            {"number": "2", "name": "GND"},
                            {"number": "3", "name": "IN"},
                            {"number": "4", "name": "OUT"},
                        ],
                    }
                ],
                "nets": [
                    {"id": "VCC", "connections": [{"component": "U1", "pin": "1"}]},
                    {"id": "GND", "connections": [{"component": "U1", "pin": "2"}]},
                ],
            }
        }

        results["validate"] = self.test_endpoint(
            "POST", "/netlist/validate", json=sample_netlist
        )

        # Upload netlist
        upload_data = {
            "netlist": sample_netlist["netlist"],
            "user_id": "test_user",
            "filename": "test_netlist.json",
        }

        results["upload"] = self.test_endpoint(
            "POST", "/netlist/upload", json=upload_data
        )

        return results

    def run_all_tests(self) -> dict[str, Any]:
        """Run all API tests"""
        self.log("🚀 Starting NetWiz Backend API Tests")
        self.log(f"   Target: {self.base_url}")
        self.log(f"   Timestamp: {datetime.now().isoformat()}")
        print()

        all_results = {
            "health": self.test_health_endpoints(),
            "netlist": self.test_netlist_endpoints(),
        }

        return all_results

    def print_summary(self, results: dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)

        total_tests = 0
        passed_tests = 0

        for category, tests in results.items():
            print(f"\n{category.upper()}:")
            for _test_name, result in tests.items():
                total_tests += 1
                if result.get("success", False):
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"

                method = result.get("method", "N/A")
                path = result.get("path", "N/A")
                status_code = result.get("status_code", "N/A")

                print(f"  {status} {method} {path} ({status_code})")

        print(f"\n📈 RESULTS: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 All tests passed!")
            return True
        else:
            print("💥 Some tests failed!")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Test NetWiz Backend API endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  netwiz-test-api                           # Run all tests
  netwiz-test-api --endpoint health         # Test only health endpoints
  netwiz-test-api --url http://localhost:8000  # Test different URL
  netwiz-test-api --verbose                 # Show detailed output
        """,
    )

    parser.add_argument(
        "--url",
        default="http://localhost:5000",
        help="Base URL of the API (default: http://localhost:5000)",
    )

    parser.add_argument(
        "--endpoint",
        choices=["health", "netlist", "all"],
        default="all",
        help="Which endpoints to test (default: all)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )

    args = parser.parse_args()

    tester = APITester(args.url, args.verbose)

    if args.endpoint == "all":
        results = tester.run_all_tests()
    elif args.endpoint == "health":
        results = {"health": tester.test_health_endpoints()}
    elif args.endpoint == "netlist":
        results = {"netlist": tester.test_netlist_endpoints()}

    success = tester.print_summary(results)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
