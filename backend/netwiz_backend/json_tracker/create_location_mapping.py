import json
from typing import Any

from json_source_map import calculate  # pip install json-source-map

from netwiz_backend.json_tracker.errors import TrackedJSONDecodeError
from netwiz_backend.json_tracker.helpers import (
    _ancestors_of,
    _infer_kind,
    _last_segment,
    _line_length_at,
    _resolve_pointer,
)
from netwiz_backend.json_tracker.self_test import self_test_locations
from netwiz_backend.json_tracker.types import LocationInfo

# ── Public API ──────────────────────────────────────────────────────────────────


def create_location_mapping(
    json_text: str, raise_on_error: bool = False, self_test: bool = True
) -> dict[str, LocationInfo]:
    """
    Build a mapping of dot-path -> LocationInfo for every JSON value and object key.

    This function uses the excellent `json-source-map` library to calculate precise
    source positions, then enhances the results with hierarchical parent relationships
    and additional metadata. The json-source-map library does the core work of
    parsing JSON and tracking character/line positions for every element.

    Paths:
      - Root value: "$"
      - Object fields: "$.user.name", "$.user.address.0.city"
      - Array indices: "$.0", "$.1", etc.

    Args:
        json_text: The JSON string to analyze
        raise_on_error: If True, raise TrackedJSONDecodeError on parse errors.
                       If False, return a synthetic error LocationInfo
        self_test: If True, run internal validation checks on the location mapping

    Returns:
        Dictionary mapping dot paths to LocationInfo objects

    Raises:
        TrackedJSONDecodeError: If raise_on_error=True and JSON is invalid

    Note:
        This function heavily relies on the `json-source-map` library for the
        core source mapping functionality. We extend it with parent relationships
        and additional metadata for our specific use case.
    """
    # Try to parse; if it fails, emit a synthetic error LocationInfo and return early.
    try:
        data: Any = json.loads(json_text)
    except json.JSONDecodeError as e:
        err_path = "$.__error__"
        # Convert Python's 0-based absolute pos and 1-based line/col into our 1-based fields.
        abs_start = e.pos + 1
        # We create a 1-char span at the error site; callers can expand if desired.
        abs_end = min(len(json_text), e.pos + 1) + 1 if len(json_text) > 0 else 1

        error_loc = LocationInfo(
            parents=[
                LocationInfo(
                    parents=[],
                    key="$",
                    kind="object",
                    start_character_number=1,
                    start_line_number=1,
                    start_line_character_number=1,
                    end_character_number=max(1, len(json_text)),
                    end_line_number=e.lineno,  # best-effort: end at error line
                    end_line_character_number=e.colno,
                )
            ],
            key="__error__",
            kind="string",
            start_character_number=abs_start,
            start_line_number=e.lineno,
            start_line_character_number=e.colno,
            end_character_number=abs_end,
            end_line_number=e.lineno,
            end_line_character_number=min(
                e.colno + 1, max(1, _line_length_at(json_text, e.lineno))
            ),
        )
        if raise_on_error:
            raise TrackedJSONDecodeError(error_loc, json_text) from e
        return {err_path: error_loc}

    # Build source map once
    entries = calculate(json_text)

    # We’ll create LocationInfo instances for every pointer (value) and its key.
    # To populate `parents`, we need a second pass to link to parents by path.
    path_to_loc: dict[str, LocationInfo] = {}
    pointer_mapping: dict[str, str] = {}

    # Helper to convert RFC6901 pointer to our dot-path
    def pointer_to_path(ptr: str) -> str:
        if not ptr:
            return "$"
        parts = ptr.lstrip("/").split("/")
        out: list[str] = []
        for p in parts:
            key = p.replace("~1", "/").replace("~0", "~")
            out.append(key if not out else f".{key}")
        return "$." + "".join(out)

    # First pass: create LocationInfo objects without parents (we’ll fill them later)
    for pointer, entry in entries.items():
        dot_path = pointer_to_path(pointer)
        pointer_mapping[pointer] = dot_path

        # Value entry
        if entry.value_start and entry.value_end:
            vs, ve = entry.value_start, entry.value_end
            val = _resolve_pointer(data, pointer)  # ← add this line
            path_to_loc[dot_path] = LocationInfo(
                parents=[],  # fill later
                key=_last_segment(dot_path),
                kind=_infer_kind(val),
                start_character_number=vs.position + 1,
                start_line_number=vs.line + 1,
                start_line_character_number=vs.column + 1,
                end_character_number=ve.position + 1,
                end_line_number=ve.line + 1,
                end_line_character_number=ve.column + 1,
            )

        # Key entry (for object members)
        if entry.key_start and entry.key_end:
            ks, ke = entry.key_start, entry.key_end
            key_path = dot_path  # same path; distinguish via kind="key"
            path_to_loc[f"{key_path}.__key__"] = LocationInfo(
                parents=[],  # fill later
                key=_last_segment(dot_path),
                kind="key",
                start_character_number=ks.position + 1,
                start_line_number=ks.line + 1,
                start_line_character_number=ks.column + 1,
                end_character_number=ke.position + 1,
                end_line_number=ke.line + 1,
                end_line_character_number=ke.column + 1,
            )

    # Second pass: wire up parents (oldest → newest).
    # For "$.a.b.0.c", parents are: ["$", "$.a", "$.a.b", "$.a.b.0"]
    for path, loc in path_to_loc.items():
        if path == "$":
            continue
        parents_chain = []
        for ancestor in _ancestors_of(path):
            anc_loc_value = path_to_loc.get(
                ancestor
            )  # prefer value node as structural parent
            if anc_loc_value:
                parents_chain.append(anc_loc_value)
        loc.parents = parents_chain

    if self_test:
        self_test_locations(json_text, path_to_loc)

    return path_to_loc


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

    locations = create_location_mapping(demo_json)

    print("\n🧭 Location mapping demo:\n")
    for path, loc in locations.items():
        print(
            f"{path:20} | kind={loc.kind:5} | "
            f"lines {loc.start_line_number}:{loc.start_line_character_number} "
            f"→ {loc.end_line_number}:{loc.end_line_character_number}"
        )
        if loc.parents:
            chain = " → ".join(p.key for p in loc.parents)
            print(f"   parents: {chain}")
