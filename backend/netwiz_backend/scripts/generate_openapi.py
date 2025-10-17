#!/usr/bin/env python3
"""
Generate OpenAPI schema for the NetWiz Backend API

This script generates a complete OpenAPI 3.0 specification from the FastAPI application
and saves it as a JSON file. The schema includes all endpoints, Pydantic models,
validation rules, and documentation.

Usage:
    python scripts/generate_openapi.py
    python scripts/generate_openapi.py --output custom_schema.json
"""

import argparse
import json
import sys
from pathlib import Path

from netwiz_backend.main import app


def main():
    """Main function to generate OpenAPI schema"""
    parser = argparse.ArgumentParser(
        description="Generate OpenAPI schema for NetWiz Backend API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/generate_openapi.py                    # Generate with default filename
  python scripts/generate_openapi.py --output api.json  # Generate with custom filename
  python scripts/generate_openapi.py --pretty           # Generate with pretty formatting
        """,
    )

    parser.add_argument(
        "--output",
        "-o",
        default="openapi.json",
        help="Output filename for the OpenAPI schema (default: openapi.json)",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Generate pretty-formatted JSON with indentation",
    )

    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for the schema file (default: backend directory)",
    )

    args = parser.parse_args()

    try:
        # Generate the OpenAPI schema
        print("🔄 Generating OpenAPI schema...")
        schema = app.openapi()

        # Prepare output path (default to backend directory)
        if args.output_dir == ".":
            # Get the backend directory (two levels up from this script)
            backend_dir = Path(__file__).parent.parent.parent
            output_dir = backend_dir
        else:
            output_dir = Path(args.output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / args.output

        # Write schema to file
        with open(output_path, "w") as f:
            if args.pretty:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            else:
                json.dump(schema, f, separators=(",", ":"), ensure_ascii=False)

        print("✅ OpenAPI schema generated successfully!")
        print(f"📁 Output file: {output_path}")
        print("📊 Schema info:")
        print(f"   - Title: {schema.get('info', {}).get('title', 'N/A')}")
        print(f"   - Version: {schema.get('info', {}).get('version', 'N/A')}")
        print(f"   - Endpoints: {len(schema.get('paths', {}))}")
        print(
            f"   - Components: {len(schema.get('components', {}).get('schemas', {}))}"
        )

        # Note: OpenAPI schema generation is handled by this script

    except Exception as e:
        print(f"❌ Error generating OpenAPI schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
