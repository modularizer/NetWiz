import json

from netwiz_backend.json_tracker.types import LocationInfo


def self_test_locations(
    json_text: str, locations: dict[str, LocationInfo]
) -> list[str]:
    """
    Validate the accuracy of location mappings by running consistency checks.

    This function performs comprehensive validation of the location data generated
    by `json-source-map` to ensure the character positions, line/column numbers,
    and hierarchical relationships are accurate and consistent.

    Args:
        json_text: The original JSON text
        locations: Location mapping from create_location_mapping()

    Returns:
        List of human-readable problems found. Empty list means all checks passed.

    Note:
        This validation helps ensure the accuracy of the source mapping provided
        by the `json-source-map` library, which does the core work of tracking
        JSON element positions.
    """
    problems: list[str] = []

    # Precompute 0-based absolute start for each 1-based line
    # keepends=True preserves exact newline widths
    lines = json_text.splitlines(keepends=True)
    line_starts: list[int] = []
    acc = 0
    for ln in lines:
        line_starts.append(acc)
        acc += len(ln)
    if not lines:
        # empty input edge case
        line_starts.append(0)

    def abs_from_line_col(line_no_1b: int, col_no_1b: int) -> int:
        # Convert 1-based line/column to 0-based absolute index
        line_idx = max(1, min(line_no_1b, len(line_starts))) - 1
        return line_starts[line_idx] + (col_no_1b - 1)

    # Build quick index of children by parent path (value nodes only)
    value_paths = [
        p
        for p, loc in locations.items()
        if not p.endswith(".__key__")
        and loc.kind in {"object", "list", "null", "string", "boolean", "number"}
    ]

    def children_of(path: str) -> list[str]:
        prefix = "$." if path == "$" else path + "."
        return [p for p in value_paths if p.startswith(prefix)]

    # Main per-location checks
    for path, loc in locations.items():
        # 1) slice by absolute character numbers (1-based, end exclusive)
        try:
            s_abs = json_text[loc.start_character_number - 1 : loc.end_character_number]
        except Exception as e:
            problems.append(f"{path}: absolute slice error: {e}")
            continue

        # 2) slice by line/col (convert to absolute, end exclusive)
        try:
            start_idx = abs_from_line_col(
                loc.start_line_number, loc.start_line_character_number
            )
            end_idx = abs_from_line_col(
                loc.end_line_number, loc.end_line_character_number
            )
            s_line = json_text[start_idx:end_idx]
        except Exception as e:
            problems.append(f"{path}: line/col slice error: {e}")
            continue

        # 3) both slices must match exactly
        if s_abs != s_line:
            problems.append(
                f"{path}: absolute vs line/col slice mismatch: {s_abs!r} != {s_line!r}"
            )

        content = s_abs  # canonical slice

        # 4) key validation
        if (
            loc.kind == "key"
            and content != (expected := json.dumps(loc.key))
            and content.strip() != expected
        ):
            problems.append(
                f"{path}: key content mismatch. got {content!r}, expected {expected!r}"
            )

        # 5) value validation
        if loc.kind == "value":
            # (a) must be parsable as standalone JSON
            try:
                parsed_val = json.loads(content)
            except Exception as e:
                problems.append(f"{path}: value is not standalone-parsable JSON: {e}")
                parsed_val = None

            # (b) container children must be contained inside parent span; primitives must have none
            child_paths = children_of(path)
            if parsed_val is None:
                # can't reliably check containment without knowing primitive/compound
                continue

            is_container = loc.kind in {"object", "list"}
            if not is_container and child_paths:
                problems.append(
                    f"{path}: primitive value has children: {child_paths[:5]}{'…' if len(child_paths)>5 else ''}"
                )

            if is_container:
                for cpath in child_paths:
                    child = locations.get(cpath)
                    if not child:
                        continue
                    # Child span must be within parent span (using absolute char numbers)
                    if not (
                        loc.start_character_number
                        <= child.start_character_number
                        <= child.end_character_number
                        <= loc.end_character_number
                    ):
                        problems.append(
                            f"{path}: child {cpath} span not within parent span "
                            f"(parent {loc.start_character_number}-{loc.end_character_number}, "
                            f"child {child.start_character_number}-{child.end_character_number})"
                        )

    return problems
