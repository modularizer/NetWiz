import json
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from netwiz_backend.json_tracker import create_location_mapping
from netwiz_backend.json_tracker.errors import TrackedJSONDecodeError
from netwiz_backend.json_tracker.helpers import _get_full_location
from netwiz_backend.json_tracker.types import LocationInfo


class TrackedJson:
    """
    A JSON parser that tracks the exact location of every element in the source text.

    TrackedJson provides a mapping-like interface to navigate JSON data while maintaining
    precise location information (line/column numbers, character offsets) for every
    value and key in the JSON structure. This is particularly useful for:

    - JSON validation with precise error reporting
    - Code editors with syntax highlighting
    - Data transformation tools that need to preserve source locations
    - Debugging and analysis of JSON structures

    The class supports multiple path formats:
    - Dot notation: "$.user.name", "$.items.0.title"
    - JSON Pointers: "/user/name", "/items/0/title"
    - Relative paths: "name" (relative to current context)

    Attributes:
        json_text (str): The original JSON text that was parsed
        locations (dict[str, LocationInfo]): Mapping of paths to location information
        error (TrackedJSONDecodeError | None): Parsing error if JSON is invalid
        location (LocationInfo): Location info for the current context
        path (str): Current dot path (e.g., "$.user.name")
        level (int): Nesting level of current context

    Example:
        >>> json_text = '{"user": {"name": "Alice", "age": 30}}'
        >>> tj = TrackedJson.loads(json_text)
        >>> tj["$.user.name"].data  # "Alice"
        >>> tj["$.user.name"].start_line_number  # 1
        >>> tj["$.user.name"].end_line_number  # 1

    Note:
        This implementation builds upon the excellent `json-source-map` library,
        which provides the core functionality for tracking JSON element positions.
        We extend it with hierarchical navigation and enhanced error reporting.
    """

    @classmethod
    def load(
        cls, f: str | Path, raise_on_error: bool = False, self_test: bool = True
    ) -> "TrackedJson":
        """
        Load TrackedJson from a file.

        Args:
            f: Path to the JSON file to load
            raise_on_error: If True, raise TrackedJSONDecodeError on parse errors.
                           If False, store error in .error attribute
            self_test: If True, run internal validation checks on the location mapping

        Returns:
            TrackedJson instance with the parsed JSON and location information

        Raises:
            TrackedJSONDecodeError: If raise_on_error=True and JSON is invalid
            FileNotFoundError: If the file doesn't exist
        """
        with Path(f).open() as f:
            json_text = f.read()
        return cls(
            json_text=json_text, raise_on_error=raise_on_error, self_test=self_test
        )

    @classmethod
    def loads(
        cls, json_text: str, raise_on_error: bool = False, self_test: bool = True
    ) -> "TrackedJson":
        """
        Create TrackedJson from a JSON string.

        Args:
            json_text: The JSON string to parse
            raise_on_error: If True, raise TrackedJSONDecodeError on parse errors.
                           If False, store error in .error attribute
            self_test: If True, run internal validation checks on the location mapping

        Returns:
            TrackedJson instance with the parsed JSON and location information

        Raises:
            TrackedJSONDecodeError: If raise_on_error=True and JSON is invalid
        """
        return cls(
            json_text=json_text, raise_on_error=raise_on_error, self_test=self_test
        )

    def dumps(self):
        """
        Serialize the JSON data back to a string.

        Returns:
            JSON string representation of the data

        Raises:
            TrackedJSONDecodeError: If the original JSON was invalid
        """
        if self.error:
            raise self.error
        return json.dumps(self.data)

    def dump(self, f: str | Path) -> None:
        """
        Write the JSON data to a file.

        Args:
            f: Path where to write the JSON file

        Raises:
            TrackedJSONDecodeError: If the original JSON was invalid
        """
        if self.error:
            raise self.error
        with Path(f).open(mode="w") as f:
            json.dump(self.data, f)

    def to_json(self) -> str:
        """
        Export all location information as a JSON string.

        This method creates a comprehensive JSON representation of all the location
        data tracked by this TrackedJson instance, including:
        - The original JSON data
        - Location information for every element
        - Parent-child relationships using indexes

        Returns:
            JSON string containing all location information

        Raises:
            TrackedJSONDecodeError: If the original JSON was invalid
        """
        if self.error:
            raise self.error

        # Build the location data structure
        location_data = {
            "original_data": self.data,
            "original_text": self.json_text,
            "locations": {},
            "error": None,
        }

        # Create a mapping of LocationInfo objects to their indexes
        location_to_index = {}
        for i, location_info in enumerate(self.locations.values()):
            location_to_index[location_info] = i

        # Convert all LocationInfo objects to dictionaries
        for path, location_info in self.locations.items():
            # Get parent indexes instead of full objects
            parent_indexes = [location_to_index[p] for p in location_info.parents]

            location_data["locations"][path] = {
                "key": location_info.key,
                "kind": location_info.kind,
                "level": location_info.level,
                "start_character_number": location_info.start_character_number,
                "start_line_number": location_info.start_line_number,
                "start_line_character_number": location_info.start_line_character_number,
                "end_character_number": location_info.end_character_number,
                "end_line_number": location_info.end_line_number,
                "end_line_character_number": location_info.end_line_character_number,
                "parent_indexes": parent_indexes,
            }

        return json.dumps(location_data, indent=2)

    def __init__(
        self,
        json_text: str,
        raise_on_error: bool = False,
        self_test: bool = True,
        _locations: dict[str, LocationInfo] | None = None,
        _location: LocationInfo | None = None,
        _path: str | None = None,
    ) -> None:
        """
        Initialize TrackedJson instance.

        Args:
            json_text: The JSON string to parse
            raise_on_error: If True, raise TrackedJSONDecodeError on parse errors.
                           If False, store error in .error attribute
            self_test: If True, run internal validation checks on the location mapping
            _locations: Internal parameter for creating sub-contexts
            _location: Internal parameter for creating sub-contexts
            _path: Internal parameter for creating sub-contexts
        """
        self.json_text = json_text
        self.locations: dict[str, LocationInfo] = _locations or create_location_mapping(
            json_text, raise_on_error=raise_on_error, self_test=self_test
        )

        # fix: check the synthesized error node path actually used by the builder
        if (
            not raise_on_error
            and len(self.locations) == 1
            and list(self.locations.keys())[0] == "$.__error__"
        ):
            error_loc = self.locations["$.__error__"]
            self.error = TrackedJSONDecodeError(error_loc, json_text)
        else:
            self.error = None

        # current node (default = root "$")
        self.location: LocationInfo = _location or self.locations.get(
            "$", _get_full_location(json_text)
        )
        self.path: str = _path or "$"
        self.level: int = getattr(self.location, "level", 0)

        # precompute line starts…
        self._lines = json_text.splitlines(keepends=True)
        self._line_starts: list[int] = []
        acc = 0
        for ln in self._lines:
            self._line_starts.append(acc)
            acc += len(ln)
        if not self._lines:
            self._line_starts.append(0)

    def _direct_child_locs(self) -> dict[str, LocationInfo]:
        """
        Get direct child locations for the current context.

        Returns:
            Dictionary mapping child names to their LocationInfo objects.
            Only includes value children, not key metadata (e.g., excludes 'x.__key__')
        """
        out: dict[str, LocationInfo] = {}
        me = self.location
        for p, loc in self.locations.items():
            if p.endswith(".__key__"):
                continue
            # direct child if my LocationInfo is the immediate parent (last in parents)
            if loc.parents and loc.parents[-1] == me:
                out[loc.key] = loc
        return out

    def _loc_for_absolute_path(self, abs_path: str) -> LocationInfo:
        """
        Get LocationInfo for an absolute dot path.

        Args:
            abs_path: Absolute dot path (e.g., "$.user.name")

        Returns:
            LocationInfo object for the specified path

        Raises:
            KeyError: If the path doesn't exist
        """
        loc = self.locations.get(abs_path)
        if not loc:
            raise KeyError(abs_path)
        return loc

    def _abs_from_relative(self, rel: str) -> str:
        """
        Convert a relative path to an absolute dot path.

        Args:
            rel: Relative path (e.g., "name", "0", "a.b")

        Returns:
            Absolute dot path (e.g., "$.user.name")
        """
        if rel.startswith("$") or rel.startswith("/"):
            # already absolute (dot path or pointer) — normalize like before
            return self._normalize_path(rel)
        return (
            "$"
            if rel == ""
            else (f"{self.path}.{rel}" if self.path != "$" else "$." + rel)
        )

    def _normalize_path(self, path: str) -> str:
        """
        Normalize a user-supplied path into internal dot-path format.

        Supports multiple path formats:
        - "$" (root)
        - "user.name" (dot path)
        - "/user/name" (JSON Pointer)
        - "name" (relative to current context)

        Args:
            path: Path to normalize

        Returns:
            Normalized dot path
        """
        if not path:
            return self.path

        # JSON Pointer → dot path
        if path.startswith("/"):
            return self._pointer_to_dot(path)

        # already absolute
        if path.startswith("$"):
            return path

        # relative path (e.g. "name" inside "$.user")
        if self.path == "$":
            return f"$.{path}"
        return f"{self.path}.{path}"

    @staticmethod
    def _pointer_to_dot(ptr: str) -> str:
        """
        Convert a JSON Pointer (RFC 6901) to dot notation.

        Examples:
            ""            -> "$"
            "/"           -> "$"
            "/user/name"  -> "$.user.name"
            "/items/0/id" -> "$.items.0.id"

        Args:
            ptr: JSON Pointer string

        Returns:
            Dot notation path
        """
        if not ptr or ptr == "/":
            return "$"

        parts = ptr.lstrip("/").split("/")
        # unescape per RFC 6901: "~1" → "/", "~0" → "~"
        decoded = [p.replace("~1", "/").replace("~0", "~") for p in parts]
        return "$." + ".".join(decoded)

    # ── Mapping dunders ────────────────────────────────────────────────────────
    def __getitem__(self, key: str | int) -> "TrackedJson":
        """
        Access JSON elements using bracket notation.

        Supports both direct child access and absolute path navigation:
        - tj["user"] - access direct child
        - tj["$.user.name"] - access nested element using absolute path
        - tj["/user/name"] - access using JSON Pointer

        Args:
            key: Child name, index, or path

        Returns:
            TrackedJson instance for the accessed element

        Raises:
            KeyError: If the key doesn't exist
        """
        name = str(key)
        # allow absolute lookups like "user.name" from root instance
        if name.startswith("$") or name.startswith("/"):
            abs_path = self._normalize_path(name)
            loc = self._loc_for_absolute_path(abs_path)
            return TrackedJson(
                self.json_text, _locations=self.locations, _location=loc, _path=abs_path
            )

        if self.location.kind == "string":
            return self.to_value()[key]

        # hierarchical: only direct children
        child = self._direct_child_locs().get(name)
        if not child:
            raise KeyError(name)
        child_abs_path = (f"{self.path}.{name}") if self.path != "$" else "$." + name
        return TrackedJson(
            self.json_text,
            _locations=self.locations,
            _location=child,
            _path=child_abs_path,
        )

    def __contains__(self, key: object) -> bool:
        """
        Check if a key exists in the current context.

        Supports both direct child access and absolute path checking:
        - "user" - check if direct child exists
        - "$.user.name" - check if absolute path exists
        - "/user/name" - check if JSON Pointer path exists

        Args:
            key: Key to check for

        Returns:
            True if the key exists as a direct child or absolute path
        """
        if not isinstance(key, str | int):
            return False

        name = str(key)
        # Check absolute paths (starting with "$" or "/")
        if name.startswith("$") or name.startswith("/"):
            abs_path = self._normalize_path(name)
            return abs_path in self.locations

        # Check direct children
        return name in self._direct_child_locs()

    def __len__(self) -> int:
        """
        Get the number of direct children in the current context.

        Returns:
            Number of direct children
        """
        return len(self._direct_child_locs())

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over direct child names in the current context.

        Returns:
            Iterator of child names
        """
        return iter(self._direct_child_locs())

    def __bool__(self) -> bool:
        """
        Check if the current element has a truthy value.

        Returns:
            True if the data is truthy
        """
        return bool(self.data)

    def __int__(self) -> int:
        """
        Convert the current element to an integer.

        Returns:
            Integer representation of the data

        Raises:
            ValueError: If the data cannot be converted to int
        """
        return int(self.data)

    def __float__(self) -> float:
        """
        Convert the current element to a float.

        Returns:
            Float representation of the data

        Raises:
            ValueError: If the data cannot be converted to float
        """
        return float(self.data)

    def __eq__(self, other: object) -> bool:
        """
        Compare the current element's data with another value.

        Args:
            other: Value to compare with

        Returns:
            True if the data equals the other value
        """
        return self.data == other

    def __ne__(self, other: object) -> bool:
        """
        Check if the current element's data is not equal to another value.

        Args:
            other: Value to compare with

        Returns:
            True if the data is not equal to the other value
        """
        return self.data != other

    def __str__(self) -> str:
        """
        Convert the current element's data to a string.

        Returns:
            String representation of the data
        """
        return str(self.data)

    # dict-like convenience (hierarchical)
    def keys(self) -> Iterable[str]:
        """
        Get all direct child keys in the current context.

        Returns:
            Iterable of child keys
        """
        return self._direct_child_locs().keys()

    def items(self) -> Iterable[tuple[str, "TrackedJson"]]:
        """
        Get all direct child key-value pairs in the current context.

        Returns:
            Iterable of (key, TrackedJson) tuples
        """
        for name, loc in self._direct_child_locs().items():
            abs_path = (f"{self.path}.{name}") if self.path != "$" else "$." + name
            yield (
                name,
                TrackedJson(
                    self.json_text,
                    _locations=self.locations,
                    _location=loc,
                    _path=abs_path,
                ),
            )

    def values(self) -> Iterable["TrackedJson"]:
        """
        Get all direct child values in the current context.

        Returns:
            Iterable of TrackedJson instances
        """
        for _, child in self.items():
            yield child

    def get(self, key: str | int, default: Any = None) -> Any:
        """
        Get a child element with a default value if not found.

        Args:
            key: Child key to look up
            default: Default value to return if key not found

        Returns:
            TrackedJson instance for the key, or default value
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __repr__(self) -> str:
        """
        Get a string representation of the TrackedJson instance.

        Returns:
            String showing the status, path, location, and value
        """
        kind = "OK" if self.data is not None else "SYNTAX_ERROR"
        return f"TrackedJson<{kind}> path={self.path!r} loc=[{self.start}:{self.end}] value={self.data!r}"

    @property
    def start(self) -> int:
        """
        Get the 0-based start character position of the current element.

        Returns:
            Start character index in the original JSON text
        """
        return self.location.start_character_number - 1

    @property
    def end(self) -> int:
        """
        Get the 0-based end character position of the current element.

        Returns:
            End character index in the original JSON text
        """
        return self.location.end_character_number - 1

    def to_string(self) -> str:
        """
        Get the raw JSON text for the current element.

        Returns:
            The substring of the original JSON text that represents this element
        """
        s = self.json_text[self.start : self.end]
        return s

    def to_value(self) -> Any:
        """
        Parse and return the Python value for the current element.

        Returns:
            Python object (dict, list, str, int, float, bool, None)

        Raises:
            TrackedJSONDecodeError: If the original JSON was invalid
        """
        if self.error:
            raise self.error
        return json.loads(self.to_string())

    @property
    def data(self) -> Any:
        """
        Get the Python value for the current element (alias for to_value).

        Returns:
            Python object (dict, list, str, int, float, bool, None)
        """
        return self.to_value()

    @property
    def raw(self) -> str:
        """
        Get the raw JSON text for the current element (alias for to_string).

        Returns:
            The substring of the original JSON text that represents this element
        """
        return self.to_string()


dumps = TrackedJson.dumps
loads = TrackedJson.loads
load = TrackedJson.load
dump = TrackedJson.dump


if __name__ == "__main__":
    demo_json = """
    {
      "user": {
        "name": "Ada Lovelace",
        "age": 36,
        "languages": ["English", "French"]
      },
      "active": true
    }
    """

    t = TrackedJson(demo_json)
    u = t["user"]
