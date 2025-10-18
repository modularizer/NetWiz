from typing import Any

from netwiz_backend.json_tracker.types import Kind, LocationInfo


def _unescape_pointer_token(token: str) -> str:
    """
    Unescape JSON Pointer tokens according to RFC 6901.

    Converts:
    - "~1" to "/"
    - "~0" to "~"

    Args:
        token: Token to unescape

    Returns:
        Unescaped token
    """
    return token.replace("~1", "/").replace("~0", "~")


def _resolve_pointer(data: Any, pointer: str) -> Any:
    """
    Resolve a JSON Pointer to get the referenced value.

    Args:
        data: The JSON data to navigate
        pointer: JSON Pointer string (e.g., "/user/name")

    Returns:
        The value at the specified pointer

    Raises:
        KeyError: If the pointer path doesn't exist
        ValueError: If trying to access list with non-integer key
    """
    if pointer == "" or pointer == "/":
        return data
    cur = data
    for part in pointer.lstrip("/").split("/"):
        key = _unescape_pointer_token(part)
        cur = cur[int(key)] if isinstance(cur, list) else cur[key]
    return cur


def _infer_kind(val: Any) -> Kind:
    """
    Infer the JSON kind from a Python value.

    Args:
        val: Python value to classify

    Returns:
        JSON kind string ("object", "list", "null", "string", "boolean", "number")
    """
    if isinstance(val, dict):
        return "object"
    if isinstance(val, list):
        return "list"
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "boolean"
    if isinstance(val, int | float):
        return "number"
        return "number"
    return "string"


def _last_segment(dot_path: str) -> str:
    """
    Extract the last segment from a dot path.

    Args:
        dot_path: Dot notation path (e.g., "$.user.name")

    Returns:
        Last segment of the path (e.g., "name")
    """
    if dot_path == "$":
        return "$"
    return dot_path.split(".")[-1]


def _ancestors_of(dot_path: str) -> list[str]:
    """
    Get all ancestor paths for a given dot path.

    For example, "$.user.name" returns ["$", "$.user"]

    Args:
        dot_path: Dot notation path

    Returns:
        List of ancestor paths from root to immediate parent
    """
    # For "$.user.name" → ["$", "$.user"]
    if dot_path == "$":
        return []
    parts = dot_path.split(".")  # ["$", "user", "name"]
    # build cumulative prefixes, excluding self
    ancestors = []
    for i in range(1, len(parts)):
        ancestors.append(".".join(parts[:i]))
    return ancestors


def _line_length_at(text: str, one_based_line: int) -> int:
    """
    Get the length of a specific line in the text.

    Args:
        text: The full text
        one_based_line: 1-based line number

    Returns:
        Length of the specified line
    """
    lines = text.splitlines() or [""]
    idx = max(1, min(one_based_line, len(lines))) - 1
    return len(lines[idx]) if 0 <= idx < len(lines) else 1


def _get_full_location(text: str) -> LocationInfo:
    """
    Create a LocationInfo for the entire text.

    Args:
        text: The full JSON text

    Returns:
        LocationInfo spanning the entire text
    """
    lines = text.splitlines() or [""]
    last_line = lines[-1]
    return LocationInfo(
        parents=[],
        key="$",
        kind="key",
        start_character_number=1,
        start_line_number=1,
        start_line_character_number=1,
        end_character_number=len(text),
        end_line_number=len(lines),
        end_line_character_number=len(last_line),
    )
