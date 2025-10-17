#!/usr/bin/env python3
"""
Generate OpenAPI schema for the NetWiz Backend API

This script generates a complete OpenAPI 3.0 specification from the FastAPI application
and saves it as a JSON file. The schema includes all endpoints, Pydantic models,
validation rules, and documentation. It also enhances the schema with better examples
for improved Swagger UI display.

Usage:
    python scripts/generate_openapi.py
    python scripts/generate_openapi.py --output custom_schema.json
"""

import argparse
import json
import sys
from pathlib import Path

from netwiz_backend.main import app


def enhance_openapi_schema(schema: dict) -> dict:
    """
    Enhance the OpenAPI schema with better examples and descriptions for Swagger UI.

    Args:
        schema: The OpenAPI schema dictionary

    Returns:
        Enhanced OpenAPI schema dictionary
    """
    # Add better examples to key schemas
    enhanced_examples = {
        "Netlist-Input": {
            "description": "Complete netlist representing an electronic circuit",
            "examples": [
                {
                    "summary": "Simple MCU Circuit",
                    "description": "A basic microcontroller circuit with power and ground",
                    "value": {
                        "components": [
                            {
                                "id": "U1",
                                "type": "IC",
                                "pins": [
                                    {"number": "1", "name": "VCC", "type": "power"},
                                    {"number": "2", "name": "GND", "type": "ground"},
                                    {"number": "3", "name": "CLK", "type": "input"},
                                ],
                                "value": "3.3V",
                                "package": "QFP-32",
                                "manufacturer": "STMicroelectronics",
                                "part_number": "STM32F103C8T6",
                            },
                            {
                                "id": "R1",
                                "type": "RESISTOR",
                                "pins": [{"number": "1"}, {"number": "2"}],
                                "value": "10kΩ",
                                "package": "0603",
                            },
                        ],
                        "nets": [
                            {
                                "id": "VCC",
                                "connections": [
                                    {"component": "U1", "pin": "1"},
                                    {"component": "R1", "pin": "1"},
                                ],
                                "net_type": "power",
                            },
                            {
                                "id": "GND",
                                "connections": [
                                    {"component": "U1", "pin": "2"},
                                    {"component": "R1", "pin": "2"},
                                ],
                                "net_type": "ground",
                            },
                        ],
                        "metadata": {
                            "designer": "John Doe",
                            "version": "1.0",
                            "description": "Simple MCU circuit with pull-up resistor",
                        },
                    },
                },
                {
                    "summary": "Power Supply Circuit",
                    "description": "A power supply circuit with voltage regulation",
                    "value": {
                        "components": [
                            {
                                "id": "U1",
                                "type": "IC",
                                "pins": [
                                    {"number": "1", "name": "VIN", "type": "input"},
                                    {"number": "2", "name": "VOUT", "type": "output"},
                                    {"number": "3", "name": "GND", "type": "ground"},
                                ],
                                "value": "5V",
                                "package": "TO-220",
                                "manufacturer": "Linear Technology",
                                "part_number": "LM7805",
                            },
                            {
                                "id": "C1",
                                "type": "CAPACITOR",
                                "pins": [{"number": "1"}, {"number": "2"}],
                                "value": "100µF",
                                "package": "0805",
                            },
                        ],
                        "nets": [
                            {
                                "id": "VIN",
                                "connections": [
                                    {"component": "U1", "pin": "1"},
                                    {"component": "C1", "pin": "1"},
                                ],
                                "net_type": "power",
                            },
                            {
                                "id": "VOUT",
                                "connections": [{"component": "U1", "pin": "2"}],
                                "net_type": "power",
                            },
                            {
                                "id": "GND",
                                "connections": [
                                    {"component": "U1", "pin": "3"},
                                    {"component": "C1", "pin": "2"},
                                ],
                                "net_type": "ground",
                            },
                        ],
                    },
                },
            ],
        },
        "Netlist-Output": {
            "description": "Complete netlist representing an electronic circuit",
            "examples": [
                {
                    "summary": "Simple MCU Circuit",
                    "description": "A basic microcontroller circuit with power and ground",
                    "value": {
                        "components": [
                            {
                                "id": "U1",
                                "type": "IC",
                                "pins": [
                                    {"number": "1", "name": "VCC", "type": "power"},
                                    {"number": "2", "name": "GND", "type": "ground"},
                                    {"number": "3", "name": "CLK", "type": "input"},
                                ],
                                "value": "3.3V",
                                "package": "QFP-32",
                                "manufacturer": "STMicroelectronics",
                                "part_number": "STM32F103C8T6",
                            },
                            {
                                "id": "R1",
                                "type": "RESISTOR",
                                "pins": [{"number": "1"}, {"number": "2"}],
                                "value": "10kΩ",
                                "package": "0603",
                            },
                        ],
                        "nets": [
                            {
                                "id": "VCC",
                                "connections": [
                                    {"component": "U1", "pin": "1"},
                                    {"component": "R1", "pin": "1"},
                                ],
                                "net_type": "power",
                            },
                            {
                                "id": "GND",
                                "connections": [
                                    {"component": "U1", "pin": "2"},
                                    {"component": "R1", "pin": "2"},
                                ],
                                "net_type": "ground",
                            },
                        ],
                        "metadata": {
                            "designer": "John Doe",
                            "version": "1.0",
                            "description": "Simple MCU circuit with pull-up resistor",
                        },
                    },
                }
            ],
        },
        "ValidationResult": {
            "description": "Result of netlist validation with errors and warnings",
            "examples": [
                {
                    "summary": "Valid Netlist",
                    "description": "A netlist that passes all validation rules",
                    "value": {
                        "is_valid": True,
                        "errors": [],
                        "warnings": [],
                        "validation_timestamp": "2024-01-15T10:30:00Z",
                        "validation_rules_applied": [
                            "blank_component_names",
                            "blank_net_names",
                            "unique_component_ids",
                            "unique_net_ids",
                            "gnd_connectivity",
                            "orphaned_nets",
                            "unconnected_components",
                        ],
                    },
                },
                {
                    "summary": "Invalid Netlist",
                    "description": "A netlist with validation errors",
                    "value": {
                        "is_valid": False,
                        "errors": [
                            {
                                "error_type": "duplicate_component_id",
                                "message": "Component IDs must be unique",
                                "severity": "error",
                            }
                        ],
                        "warnings": [
                            {
                                "error_type": "unconnected_component",
                                "message": "Component is not connected to any net",
                                "component_id": "R5",
                                "severity": "warning",
                            }
                        ],
                        "validation_timestamp": "2024-01-15T10:30:00Z",
                        "validation_rules_applied": [
                            "blank_component_names",
                            "blank_net_names",
                            "unique_component_ids",
                            "unique_net_ids",
                        ],
                    },
                },
            ],
        },
    }

    # Apply enhancements to schemas
    for schema_name, enhancements in enhanced_examples.items():
        if schema_name in schema["components"]["schemas"]:
            schema["components"]["schemas"][schema_name].update(enhancements)

    return schema


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

        # Enhance the schema for better Swagger UI display
        print("🎨 Enhancing schema for better Swagger UI...")
        schema = enhance_openapi_schema(schema)

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

        print("✅ OpenAPI schema generated and enhanced successfully!")
        print(f"📁 Output file: {output_path}")
        print("📊 Schema info:")
        print(f"   - Title: {schema.get('info', {}).get('title', 'N/A')}")
        print(f"   - Version: {schema.get('info', {}).get('version', 'N/A')}")
        print(f"   - Endpoints: {len(schema.get('paths', {}))}")
        print(
            f"   - Components: {len(schema.get('components', {}).get('schemas', {}))}"
        )

    except Exception as e:
        print(f"❌ Error generating OpenAPI schema: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
