from __future__ import annotations

import json
from pathlib import Path

import pytest

from netwiz_backend.json_tracker import TrackedJson, TrackedJSONDecodeError

FIXTURES = Path(__file__).parent / "fixtures"
GOOD = FIXTURES / "good"
BAD = FIXTURES / "bad"


def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ── Test Data ────────────────────────────────────────────────────────────────────

SIMPLE_JSON = """
{
  "user": {
    "name": "Alice",
    "age": 30,
    "hobbies": ["reading", "coding"]
  },
  "active": true
}
"""

NESTED_JSON = """
{
  "level1": {
    "level2": {
      "level3": {
        "value": "deep"
      }
    }
  },
  "array": [
    {"id": 1, "name": "first"},
    {"id": 2, "name": "second"}
  ]
}
"""

INVALID_JSON = '{"invalid": json}'


# ── Basic Functionality Tests ────────────────────────────────────────────────────


def test_loads_basic():
    """Test basic JSON loading and data access."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    assert tj.data == json.loads(SIMPLE_JSON)
    assert tj["user"]["name"].data == "Alice"
    assert tj["user"]["age"].data == 30
    assert tj["active"].data is True


def test_load_from_file(tmp_path):
    """Test loading JSON from a file."""
    json_file = tmp_path / "test.json"
    json_file.write_text(SIMPLE_JSON)

    tj = TrackedJson.load(json_file)
    assert tj["user"]["name"].data == "Alice"


def test_dumps_and_dump(tmp_path):
    """Test serializing back to JSON."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    # Test dumps
    dumped = tj.dumps()
    assert json.loads(dumped) == json.loads(SIMPLE_JSON)

    # Test dump to file
    output_file = tmp_path / "output.json"
    tj.dump(output_file)
    assert json.loads(output_file.read_text()) == json.loads(SIMPLE_JSON)


# ── Path Navigation Tests ─────────────────────────────────────────────────────────


def test_dot_notation_access():
    """Test accessing elements using dot notation."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    assert tj["$.user.name"].data == "Alice"
    assert tj["$.user.age"].data == 30
    assert tj["$.user.hobbies.0"].data == "reading"
    assert tj["$.user.hobbies.1"].data == "coding"


def test_json_pointer_access():
    """Test accessing elements using JSON Pointers."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    assert tj["/user/name"].data == "Alice"
    assert tj["/user/age"].data == 30
    assert tj["/user/hobbies/0"].data == "reading"
    assert tj["/user/hobbies/1"].data == "coding"


def test_relative_access():
    """Test accessing elements relative to current context."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    user = tj["user"]
    assert user["name"].data == "Alice"
    assert user["age"].data == 30

    hobbies = user["hobbies"]
    assert hobbies["0"].data == "reading"
    assert hobbies["1"].data == "coding"


def test_root_access():
    """Test accessing root element."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    assert tj["$"].data == json.loads(SIMPLE_JSON)
    assert tj["/"].data == json.loads(SIMPLE_JSON)


# ── Mapping Interface Tests ─────────────────────────────────────────────────────


def test_contains_operator():
    """Test the 'in' operator for both direct children and absolute paths."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    # Direct children
    assert "user" in tj
    assert "active" in tj
    assert "nonexistent" not in tj

    # Absolute paths
    assert "$.user.name" in tj
    assert "$.user.age" in tj
    assert "$.nonexistent" not in tj

    # JSON Pointers
    assert "/user/name" in tj
    assert "/user/age" in tj
    assert "/nonexistent" not in tj


def test_len_operator():
    """Test the len() function."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    assert len(tj) == 2  # "user" and "active"

    user = tj["user"]
    assert len(user) == 3  # "name", "age", "hobbies"

    hobbies = tj["user"]["hobbies"]
    assert len(hobbies) == 2  # Two hobbies


def test_iteration():
    """Test iteration over direct children."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    keys = list(tj)
    assert set(keys) == {"user", "active"}

    user_keys = list(tj["user"])
    assert set(user_keys) == {"name", "age", "hobbies"}


def test_keys_values_items():
    """Test dict-like methods."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    # Keys
    keys = list(tj.keys())
    assert set(keys) == {"user", "active"}

    # Values
    values = list(tj.values())
    assert len(values) == 2
    assert values[0].data == json.loads(SIMPLE_JSON)["user"]
    assert values[1].data is True

    # Items
    items = list(tj.items())
    assert len(items) == 2
    assert items[0][0] == "user"
    assert items[1][0] == "active"


def test_get_method():
    """Test the get() method with defaults."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    # Existing key
    user = tj.get("user")
    assert user.data == json.loads(SIMPLE_JSON)["user"]

    # Non-existing key with default
    default_val = tj.get("nonexistent", "default")
    assert default_val == "default"

    # Non-existing key without default
    none_val = tj.get("nonexistent")
    assert none_val is None


# ── Type Conversion Tests ────────────────────────────────────────────────────────


def test_type_conversion():
    """Test conversion to Python types."""
    tj = TrackedJson.loads('{"num": 42, "float": 3.14, "bool": true, "str": "hello"}')

    assert int(tj["num"]) == 42
    assert float(tj["float"]) == 3.14
    assert bool(tj["bool"]) is True
    assert str(tj["str"]) == "hello"


def test_boolean_evaluation():
    """Test boolean evaluation of elements."""
    tj = TrackedJson.loads('{"truthy": "hello", "falsy": "", "null": null, "zero": 0}')

    assert bool(tj["truthy"]) is True
    assert bool(tj["falsy"]) is False
    assert bool(tj["null"]) is False
    assert bool(tj["zero"]) is False


def test_equality_comparison():
    """Test equality comparison."""
    tj = TrackedJson.loads('{"value": "test"}')

    assert tj["value"] == "test"
    assert tj["value"] != "other"
    assert tj["value"] == tj["value"]


# ── Location Information Tests ────────────────────────────────────────────────────


def test_location_properties():
    """Test location-related properties."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    name_element = tj["$.user.name"]

    # Character positions
    assert isinstance(name_element.start, int)
    assert isinstance(name_element.end, int)
    assert name_element.end > name_element.start

    # Location info
    loc = name_element.location
    assert loc.start_line_number >= 1
    assert loc.start_line_character_number >= 1
    assert loc.end_line_number >= loc.start_line_number
    assert loc.end_line_character_number >= loc.start_line_character_number

    # Nesting level
    assert loc.level >= 0


def test_raw_text_extraction():
    """Test extracting raw JSON text for elements."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    name_element = tj["$.user.name"]
    raw_text = name_element.raw

    assert isinstance(raw_text, str)
    assert '"Alice"' in raw_text or raw_text == '"Alice"'


def test_to_string_and_to_value():
    """Test to_string() and to_value() methods."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    name_element = tj["$.user.name"]

    # to_string should return raw JSON text
    raw = name_element.to_string()
    assert isinstance(raw, str)

    # to_value should return Python value
    value = name_element.to_value()
    assert value == "Alice"


# ── Error Handling Tests ─────────────────────────────────────────────────────────


def test_invalid_json_error_handling():
    """Test handling of invalid JSON."""
    # With raise_on_error=False (default)
    tj = TrackedJson.loads(INVALID_JSON, raise_on_error=False)
    assert tj.error is not None
    assert isinstance(tj.error, TrackedJSONDecodeError)

    # With raise_on_error=True
    with pytest.raises(TrackedJSONDecodeError):
        TrackedJson.loads(INVALID_JSON, raise_on_error=True)


def test_key_error_on_nonexistent_path():
    """Test KeyError when accessing non-existent paths."""
    tj = TrackedJson.loads(SIMPLE_JSON)

    with pytest.raises(KeyError):
        tj["nonexistent"]

    with pytest.raises(KeyError):
        tj["$.nonexistent"]

    with pytest.raises(KeyError):
        tj["/nonexistent"]


def test_error_when_calling_methods_on_invalid_json():
    """Test that methods raise error when JSON is invalid."""
    tj = TrackedJson.loads(INVALID_JSON, raise_on_error=False)

    with pytest.raises(TrackedJSONDecodeError):
        tj.dumps()

    with pytest.raises(TrackedJSONDecodeError):
        tj.to_value()


# ── File-based Tests ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("file_path", sorted(GOOD.glob("*.json")))
def test_good_files_with_tracked_json(file_path: Path):
    """Test TrackedJson with all good test fixtures."""
    text = load_text(file_path)
    tj = TrackedJson.loads(text)

    # Basic assertions
    assert tj.data == json.loads(text)
    assert tj.error is None

    # Test root access
    assert tj["$"].data == json.loads(text)

    # Test that we can iterate over top-level keys
    if isinstance(json.loads(text), dict):
        for key in tj:
            assert key in json.loads(text)


@pytest.mark.parametrize("file_path", sorted(BAD.glob("*.json")))
def test_bad_files_with_tracked_json(file_path: Path):
    """Test TrackedJson with all bad test fixtures."""
    text = load_text(file_path)

    # Should not raise with raise_on_error=False
    tj = TrackedJson.loads(text, raise_on_error=False)
    assert tj.error is not None
    assert isinstance(tj.error, TrackedJSONDecodeError)

    # Should raise with raise_on_error=True
    with pytest.raises(TrackedJSONDecodeError):
        TrackedJson.loads(text, raise_on_error=True)


# ── Edge Cases Tests ─────────────────────────────────────────────────────────────


def test_empty_json():
    """Test handling of empty JSON."""
    tj = TrackedJson.loads("{}")
    assert tj.data == {}
    assert len(tj) == 0
    assert list(tj) == []


def test_single_value_json():
    """Test handling of single value JSON."""
    tj = TrackedJson.loads('"hello"')
    assert tj.data == "hello"
    assert tj.raw == '"hello"'


def test_nested_arrays():
    """Test navigation through nested arrays."""
    tj = TrackedJson.loads(NESTED_JSON)

    # Access nested array elements
    assert tj["$.array.0.id"].data == 1
    assert tj["$.array.0.name"].data == "first"
    assert tj["$.array.1.id"].data == 2
    assert tj["$.array.1.name"].data == "second"

    # Access using JSON Pointers
    assert tj["/array/0/id"].data == 1
    assert tj["/array/1/name"].data == "second"


def test_deep_nesting():
    """Test navigation through deeply nested objects."""
    tj = TrackedJson.loads(NESTED_JSON)

    # Deep nesting
    assert tj["$.level1.level2.level3.value"].data == "deep"
    assert tj["/level1/level2/level3/value"].data == "deep"

    # Check nesting level
    deep_element = tj["$.level1.level2.level3.value"]
    assert deep_element.location.level >= 3


def test_unicode_and_special_characters():
    """Test handling of unicode and special characters."""
    unicode_json = '{"name": "José", "emoji": "🚀", "quote": "He said \\"Hello\\""}'
    tj = TrackedJson.loads(unicode_json)

    assert tj["$.name"].data == "José"
    assert tj["$.emoji"].data == "🚀"
    assert tj["$.quote"].data == 'He said "Hello"'


# ── Performance and Self-test Tests ─────────────────────────────────────────────


def test_self_test_disabled():
    """Test that self_test=False works without issues."""
    tj = TrackedJson.loads(SIMPLE_JSON, self_test=False)
    assert tj.data == json.loads(SIMPLE_JSON)


def test_repr_string():
    """Test string representation."""
    tj = TrackedJson.loads(SIMPLE_JSON)
    repr_str = repr(tj)

    assert "TrackedJson" in repr_str
    assert "path=" in repr_str
    assert "loc=" in repr_str


def test_to_json_method():
    """Test the to_json method for exporting location information."""
    tj = TrackedJson.loads(SIMPLE_JSON)
    location_json = tj.to_json()

    # Parse the JSON
    location_data = json.loads(location_json)

    # Check structure
    assert "original_data" in location_data
    assert "original_text" in location_data
    assert "locations" in location_data
    assert "error" in location_data

    # Check that original data matches
    assert location_data["original_data"] == json.loads(SIMPLE_JSON)
    assert location_data["original_text"] == SIMPLE_JSON
    assert location_data["error"] is None

    # Check locations structure
    locations = location_data["locations"]
    assert "$" in locations
    assert "$.user" in locations
    assert "$.user.name" in locations
    assert "$.active" in locations

    # Check a specific location entry
    user_name = locations["$.user.name"]
    assert user_name["key"] == "name"
    assert user_name["kind"] == "string"
    assert user_name["level"] == 2
    assert "parent_indexes" in user_name
    assert isinstance(user_name["parent_indexes"], list)

    # Check that parent indexes are valid
    for parent_idx in user_name["parent_indexes"]:
        assert isinstance(parent_idx, int)
        assert 0 <= parent_idx < len(locations)


def test_to_json_with_invalid_json():
    """Test to_json method with invalid JSON."""
    tj = TrackedJson.loads(INVALID_JSON, raise_on_error=False)

    with pytest.raises(TrackedJSONDecodeError):
        tj.to_json()


# ── Integration Tests ───────────────────────────────────────────────────────────


def test_complex_navigation_scenario():
    """Test a complex navigation scenario."""
    complex_json = """
    {
      "users": [
        {
          "id": 1,
          "profile": {
            "name": "Alice",
            "settings": {
              "theme": "dark",
              "notifications": true
            }
          }
        },
        {
          "id": 2,
          "profile": {
            "name": "Bob",
            "settings": {
              "theme": "light",
              "notifications": false
            }
          }
        }
      ],
      "metadata": {
        "total": 2,
        "last_updated": "2024-01-01"
      }
    }
    """

    tj = TrackedJson.loads(complex_json)

    # Navigate through complex structure
    assert tj["$.users.0.profile.name"].data == "Alice"
    assert tj["$.users.0.profile.settings.theme"].data == "dark"
    assert tj["$.users.1.profile.name"].data == "Bob"
    assert tj["$.metadata.total"].data == 2

    # Test iteration
    users = tj["users"]
    assert len(users) == 2

    # Test contains
    assert "users" in tj
    assert "$.users.0.profile.name" in tj
    assert "/users/0/profile/settings/theme" in tj
