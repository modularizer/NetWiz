"""
JSON Tracker - A powerful library for parsing JSON while tracking element locations.

This module provides precise location tracking for JSON elements, enabling
detailed error reporting and validation with exact line/column information.
"""

from .create_location_mapping import create_location_mapping
from .errors import TrackedJSONDecodeError
from .tracked_json import TrackedJson
from .types import LocationInfo

__all__ = [
    "TrackedJson",
    "LocationInfo",
    "TrackedJSONDecodeError",
    "create_location_mapping",
]
