# JSON Tracker

A powerful Python library for parsing JSON while tracking the exact location of every element in the source text. Built on top of the excellent [`json-source-map`](https://github.com/paulgb/json-source-map) library which does the heavy lifting, this module provides precise line/column information, character offsets, and hierarchical navigation for JSON data.

## Features

- **Precise Location Tracking**: Get exact line/column numbers and character offsets for every JSON element
- **Multiple Path Formats**: Support for dot notation, JSON Pointers, and relative paths
- **Hierarchical Navigation**: Navigate JSON structures while maintaining context
- **Enhanced Error Reporting**: Detailed error messages with source location information
- **Mapping-like Interface**: Use familiar dictionary/list syntax to access JSON elements
- **Validation Support**: Built-in self-testing to ensure location accuracy

## Installation

The module requires the `json-source-map` library:

```bash
pip install json-source-map
```

## Quick Start

### Basic Usage

```python
from netwiz_backend.json_tracker import TrackedJson

# Parse JSON from string
json_text = '''
{
  "user": {
    "name": "Alice",
    "age": 30,
    "hobbies": ["reading", "coding"]
  },
  "active": true
}
'''

tj = TrackedJson.loads(json_text)

# Access data like a dictionary
print(tj["user"]["name"].data)  # "Alice"
print(tj["user"]["age"].data)   # 30

# Get location information
name_element = tj["$.user.name"]
print(f"Name starts at line {name_element.location.start_line_number}")
print(f"Name ends at column {name_element.location.end_line_character_number}")
```

### Loading from Files

```python
# Load from file
tj = TrackedJson.load("data.json")

# Save to file
tj.dump("output.json")
```

### Error Handling

```python
try:
    tj = TrackedJson.loads('{"invalid": json}')
except TrackedJSONDecodeError as e:
    print(f"Error at line {e.lineno}, column {e.colno}")
    print(f"Context: {e.snippet()}")
```

## Path Formats

The library supports multiple path formats for navigation:

### Dot Notation
```python
tj["$.user.name"]        # Access nested properties
tj["$.items.0.title"]    # Access array elements
```

### JSON Pointers (RFC 6901)
```python
tj["/user/name"]       # JSON Pointer format
tj["/items/0/title"]   # Array access with JSON Pointer
```

### Relative Paths
```python
user = tj["user"]
name = user["name"]     # Relative to current context
```

## Location Information

Every JSON element provides detailed location information:

```python
element = tj["$.user.name"]

# Character positions (0-based)
print(f"Start: {element.start}")
print(f"End: {element.end}")

# Line/column information (1-based)
loc = element.location
print(f"Line: {loc.start_line_number}")
print(f"Column: {loc.start_line_character_number}")
print(f"End line: {loc.end_line_number}")
print(f"End column: {loc.end_line_character_number}")

# Raw JSON text for this element
print(f"Raw text: {element.raw}")

# Nesting level
print(f"Nesting level: {loc.level}")
```

## Navigation Methods

### Dictionary-like Access
```python
# Check if key exists
if "user" in tj:
    print("User exists")

# Get with default
name = tj.get("user", {}).get("name", "Unknown")

# Iterate over children
for key, value in tj["user"].items():
    print(f"{key}: {value.data}")

# Get all keys/values
keys = list(tj["user"].keys())
values = list(tj["user"].values())
```

### Type Conversion
```python
# Convert to Python types
age = int(tj["$.user.age"])       # Convert to int
active = bool(tj["$.active"])     # Convert to bool
name = str(tj["$.user.name"])     # Convert to string
```

## Advanced Features

### Self-Testing
The library includes built-in validation to ensure location accuracy:

```python
# Enable self-testing (default: True)
tj = TrackedJson.loads(json_text, self_test=True)

# Disable for performance-critical applications
tj = TrackedJson.loads(json_text, self_test=False)
```

### Error Recovery
```python
# Don't raise on parse errors, store in .error attribute
tj = TrackedJson.loads(invalid_json, raise_on_error=False)
if tj.error:
    print(f"Parse error: {tj.error}")
```

### Direct Location Mapping
For advanced use cases, you can work directly with the location mapping:

```python
from netwiz_backend.json_tracker import create_location_mapping

locations = create_location_mapping(json_text)
for path, location_info in locations.items():
    print(f"{path}: {location_info.kind} at line {location_info.start_line_number}")
```

## Use Cases

### JSON Validation with Precise Error Reporting
```python
def validate_json_with_locations(json_text):
    try:
        tj = TrackedJson.loads(json_text)
        # Your validation logic here
        return True, None
    except TrackedJSONDecodeError as e:
        return False, f"Error at line {e.lineno}, column {e.colno}: {e.msg}"
```

### Code Editor Integration
```python
def highlight_json_element(tj, path):
    element = tj[path]
    return {
        "start_line": element.location.start_line_number,
        "start_col": element.location.start_line_character_number,
        "end_line": element.location.end_line_number,
        "end_col": element.location.end_line_character_number,
        "value": element.data
    }
```

### Data Transformation with Source Tracking
```python
def transform_with_locations(tj):
    results = []
    for key, value in tj.items():
        results.append({
            "key": key,
            "value": value.data,
            "location": {
                "line": value.location.start_line_number,
                "column": value.location.start_line_character_number
            }
        })
    return results
```

### Exporting Location Data
```python
def export_location_data(tj):
    # Export all location information as JSON
    location_json = tj.to_json()

    # Parse the exported data
    location_data = json.loads(location_json)

    # Access the original data and locations
    original_data = location_data["original_data"]
    locations = location_data["locations"]

    # Each location entry contains:
    # - key, kind, level
    # - start/end character numbers and line/column positions
    # - parent_indexes: list of indexes into the locations dict

    return location_data
```

## API Reference

### TrackedJson Class

#### Class Methods
- `load(f: str | Path, raise_on_error: bool = False, self_test: bool = True) -> TrackedJson`
- `loads(json_text: str, raise_on_error: bool = False, self_test: bool = True) -> TrackedJson`

#### Instance Methods
- `dumps() -> str`: Serialize back to JSON string
- `dump(f: str | Path) -> None`: Write to file
- `to_string() -> str`: Get raw JSON text for current element
- `to_value() -> Any`: Get Python value for current element
- `to_json() -> str`: Export all location information as JSON string

#### Properties
- `data`: Python value (alias for `to_value()`)
- `raw`: Raw JSON text (alias for `to_string()`)
- `start`: 0-based start character position
- `end`: 0-based end character position
- `location`: LocationInfo object with detailed position data
- `path`: Current dot path
- `level`: Nesting level
- `error`: TrackedJSONDecodeError if parsing failed

### LocationInfo Class

Represents location information for a JSON element:

- `parents`: List of parent LocationInfo objects
- `key`: Element name/key
- `kind`: JSON type ("key", "object", "list", "null", "string", "boolean", "number")
- `start_character_number`: 1-based start character position
- `start_line_number`: 1-based start line number
- `start_line_character_number`: 1-based start column number
- `end_character_number`: 1-based end character position
- `end_line_number`: 1-based end line number
- `end_line_character_number`: 1-based end column number
- `level`: Nesting depth (number of parents)

### TrackedJSONDecodeError Class

Enhanced JSON decode error with location information:

- `error_loc`: LocationInfo with error position
- `snippet(radius: int = 40) -> str`: Get context around error
- `from_stdlib_error(e: json.JSONDecodeError, json_text: str)`: Convert standard error
- `from_location(loc: LocationInfo, json_text: str, message: str)`: Create from LocationInfo

## Dependencies

This module relies heavily on the [`json-source-map`](https://github.com/paulgb/json-source-map) library for the core functionality of tracking JSON element positions. We extend it with:

- Hierarchical parent relationships
- Enhanced error reporting
- Multiple path format support
- Validation and self-testing

## Performance Notes

- Location mapping is computed once during initialization
- Self-testing adds validation overhead but ensures accuracy
- For performance-critical applications, consider disabling self-testing
- The `json-source-map` library is optimized for large JSON documents

## License

This module is part of the NetWiz project. Please refer to the main project license for usage terms.
