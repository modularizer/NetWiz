"""
JSON parser with location tracking for netlist validation.

This module provides JSON parsing capabilities that track line numbers and
character positions, enabling precise error reporting for validation issues.

Key Features:
- **Location tracking**: Tracks line numbers and character positions for all JSON elements
- **Error reporting**: Provides detailed location information for parsing errors
- **Pydantic integration**: Works seamlessly with Pydantic models for validation
- **Performance**: Efficient parsing with minimal overhead

Example:
    ```python
    from netwiz_backend.netlist.core.json_parser import parse_netlist_with_locations

    # Parse JSON with location tracking
    result = parse_netlist_with_locations(json_text)

    if result.success:
        netlist = result.data
        locations = result.locations
    else:
        print(f"Parse error at line {result.error_line}, position {result.error_position}")
    ```
"""
import json
import re
from typing import Any

from pydantic import BaseModel, Field


class LocationInfo(BaseModel):
    """
    Represents the location of a JSON element in the source text.

    Attributes:
        line_number: 1-based line number where the element starts
        character_position: 1-based character position in the line
        end_line_number: 1-based line number where the element ends
        end_character_position: 1-based character position where the element ends
    """

    line_number: int = Field(
        ..., description="1-based line number where element starts"
    )
    character_position: int = Field(
        ..., description="1-based character position in line"
    )
    end_line_number: int = Field(
        ..., description="1-based line number where element ends"
    )
    end_character_position: int = Field(
        ..., description="1-based character position where element ends"
    )


class ParseResult(BaseModel):
    """
    Result of JSON parsing with location information.

    Attributes:
        success: True if parsing was successful
        data: Parsed JSON data (if successful)
        locations: Location mapping for JSON elements (if successful)
        error_message: Error message (if failed)
        error_line: Line number where error occurred (if failed)
        error_position: Character position where error occurred (if failed)
    """

    success: bool = Field(..., description="Whether parsing was successful")
    data: dict[str, Any] | None = Field(default=None, description="Parsed JSON data")
    locations: dict[str, LocationInfo] | None = Field(
        default=None, description="Location mapping for elements"
    )
    error_message: str | None = Field(
        default=None, description="Error message if parsing failed"
    )
    error_line: int | None = Field(
        default=None, description="Line number where error occurred"
    )
    error_position: int | None = Field(
        default=None, description="Character position where error occurred"
    )


def parse_netlist_with_locations(json_text: str) -> ParseResult:
    """
    Parse netlist JSON text with location tracking.

    This function parses JSON text and provides location information for all
    elements, enabling precise error reporting during validation.

    Args:
        json_text: The JSON text to parse

    Returns:
        ParseResult with parsed data and location information

    Example:
        ```python
        result = parse_netlist_with_locations(json_text)

        if result.success:
            netlist_data = result.data
            locations = result.locations

            # Get location of a specific component
            component_location = locations.get("components.0.name")
            if component_location:
                print(f"Component name at line {component_location.line_number}")
        else:
            print(f"Parse error: {result.error_message}")
        ```
    """
    try:
        # First, parse the JSON normally
        data = json.loads(json_text)

        # Then, create a simple location mapping based on text analysis
        locations = _create_location_mapping(json_text, data)

        return ParseResult(success=True, data=data, locations=locations)

    except json.JSONDecodeError as e:
        return ParseResult(
            success=False,
            error_message=str(e),
            error_line=e.lineno if hasattr(e, "lineno") else None,
            error_position=e.colno if hasattr(e, "colno") else None,
        )
    except Exception as e:
        return ParseResult(success=False, error_message=f"Unexpected error: {e!s}")


def _create_location_mapping(json_text: str, data: Any) -> dict[str, LocationInfo]:
    """
    Create a location mapping for JSON elements by analyzing the text.

    This function recursively tracks ALL elements in ANY JSON structure,
    providing location information for every field at every level.
    Completely agnostic to structure or field names.

    Args:
        json_text: The original JSON text
        data: The parsed JSON data (any type)

    Returns:
        Dictionary mapping JSON paths to LocationInfo objects
    """
    locations = {}
    lines = json_text.split("\n")

    def _track_element(element: Any, path: str) -> None:
        """Recursively track all elements and their locations"""
        if isinstance(element, dict):
            # Track the object itself
            if path:
                element_location = _find_element_in_text(json_text, element, lines)
                if element_location:
                    locations[path] = element_location

            # Track all fields in the object
            for key, value in element.items():
                field_path = f"{path}.{key}" if path else key
                _track_element(value, field_path)

        elif isinstance(element, list):
            # Track the array itself
            if path:
                element_location = _find_element_in_text(json_text, element, lines)
                if element_location:
                    locations[path] = element_location

            # Track all items in the array
            for i, item in enumerate(element):
                item_path = f"{path}.{i}" if path else str(i)
                _track_element(item, item_path)

        else:
            # Track primitive values (strings, numbers, booleans, null)
            if path:
                if isinstance(element, str):
                    value_location = _find_string_in_text(json_text, element, lines)
                    if value_location:
                        locations[path] = value_location
                else:
                    # For non-string primitives, try to find them by searching for their JSON representation
                    primitive_location = _find_primitive_in_text(
                        json_text, element, lines
                    )
                    if primitive_location:
                        locations[path] = primitive_location

    # Start tracking from the root
    _track_element(data, "")

    return locations


def _find_element_in_text(
    json_text: str, element: Any, lines: list[str]
) -> LocationInfo | None:
    """
    Find the location of any JSON element in the text.

    Args:
        json_text: The JSON text
        element: The element to find (any type)
        lines: List of lines in the JSON text

    Returns:
        LocationInfo if found, None otherwise
    """
    if isinstance(element, dict):
        # For objects, search for the first key-value pair
        if not element:
            return None
        first_key = next(iter(element.keys()))
        search_pattern = f'"{first_key}"'
        match = re.search(search_pattern, json_text)
        if match:
            start_pos = match.start()
            return _position_to_location(start_pos, lines)

    elif isinstance(element, list):
        # For arrays, search for the opening bracket
        if not element:
            return None
        # Find the first non-whitespace character of the array
        # This is a simplified approach - we'll search for the opening bracket
        search_pattern = r"\["
        match = re.search(search_pattern, json_text)
        if match:
            start_pos = match.start()
            return _position_to_location(start_pos, lines)

    elif isinstance(element, str):
        # For strings, use the string finder
        return _find_string_in_text(json_text, element, lines)

    else:
        # For primitives, use the primitive finder
        return _find_primitive_in_text(json_text, element, lines)

    return None


def _find_string_in_text(
    json_text: str, value: str, lines: list[str]
) -> LocationInfo | None:
    """
    Find the location of a string value in the JSON text.

    Args:
        json_text: The JSON text
        value: The string value to find
        lines: List of lines in the JSON text

    Returns:
        LocationInfo if found, None otherwise
    """
    if not value:
        return None

    # Search for the string value (with quotes)
    search_pattern = f'"{re.escape(value)}"'
    match = re.search(search_pattern, json_text)

    if match:
        start_pos = match.start()
        return _position_to_location(start_pos, lines)

    return None


def _find_primitive_in_text(
    json_text: str, value: Any, lines: list[str]
) -> LocationInfo | None:
    """
    Find the location of a primitive value (number, boolean, null) in the JSON text.

    Args:
        json_text: The JSON text
        value: The primitive value to find
        lines: List of lines in the JSON text

    Returns:
        LocationInfo if found, None otherwise
    """
    if value is None:
        # Search for null
        search_pattern = r"\bnull\b"
    elif isinstance(value, bool):
        # Search for true/false
        search_pattern = r"\b(true|false)\b"
    elif isinstance(value, int | float):
        # Search for the number
        search_pattern = re.escape(str(value))
    else:
        return None

    match = re.search(search_pattern, json_text)
    if match:
        start_pos = match.start()
        return _position_to_location(start_pos, lines)

    return None


def _position_to_location(position: int, lines: list[str]) -> LocationInfo:
    """
    Convert a character position to line and character information.

    Args:
        position: Character position in the text
        lines: List of lines

    Returns:
        LocationInfo with line and character positions
    """
    current_pos = 0

    for line_num, line in enumerate(lines, 1):
        line_end = current_pos + len(line)

        if position >= current_pos and position < line_end:
            char_pos = position - current_pos + 1
            return LocationInfo(
                line_number=line_num,
                character_position=char_pos,
                end_line_number=line_num,
                end_character_position=char_pos + 1,
            )

        current_pos = line_end + 1  # +1 for newline

    # Fallback to last line
    return LocationInfo(
        line_number=len(lines),
        character_position=1,
        end_line_number=len(lines),
        end_character_position=1,
    )


def find_element_location(
    locations: dict[str, LocationInfo], path: str
) -> LocationInfo | None:
    """
    Find the location of a specific JSON element.

    Args:
        locations: Location mapping from parse_netlist_with_locations
        path: JSON path to the element (e.g., "components.0.name")

    Returns:
        LocationInfo if found, None otherwise

    Example:
        ```python
        result = parse_netlist_with_locations(json_text)
        if result.success:
            location = find_element_location(result.locations, "components.0.name")
            if location:
                print(f"Element at line {location.line_number}, position {location.character_position}")
        ```
    """
    return locations.get(path)


def get_location_for_component(
    locations: dict[str, LocationInfo], component_index: int
) -> LocationInfo | None:
    """
    Get the location of a specific component in the netlist.

    Args:
        locations: Location mapping from parse_netlist_with_locations
        component_index: Index of the component in the components array

    Returns:
        LocationInfo for the component if found, None otherwise
    """
    return locations.get(f"components.{component_index}")


def get_location_for_net(
    locations: dict[str, LocationInfo], net_index: int
) -> LocationInfo | None:
    """
    Get the location of a specific net in the netlist.

    Args:
        locations: Location mapping from parse_netlist_with_locations
        net_index: Index of the net in the nets array

    Returns:
        LocationInfo for the net if found, None otherwise
    """
    return locations.get(f"nets.{net_index}")


def get_location_for_component_name(
    locations: dict[str, LocationInfo], component_index: int
) -> LocationInfo | None:
    """
    Get the location of a component's name field.

    Args:
        locations: Location mapping from parse_netlist_with_locations
        component_index: Index of the component in the components array

    Returns:
        LocationInfo for the component name if found, None otherwise
    """
    return locations.get(f"components.{component_index}.name")


def get_location_for_net_name(
    locations: dict[str, LocationInfo], net_index: int
) -> LocationInfo | None:
    """
    Get the location of a net's name field.

    Args:
        locations: Location mapping from parse_netlist_with_locations
        net_index: Index of the net in the nets array

    Returns:
        LocationInfo for the net name if found, None otherwise
    """
    return locations.get(f"nets.{net_index}.name")
