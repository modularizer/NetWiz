from __future__ import annotations

from pathlib import Path

import pytest

# Import your implementation
# Adjust import to where you defined it (e.g., from mypkg.json_tracker import create_location_mapping, LocationInfo)
from netwiz_backend.json_tracker import LocationInfo, create_location_mapping

FIXTURES = Path(__file__).parent / "fixtures"
GOOD = FIXTURES / "good"
BAD = FIXTURES / "bad"


def load_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ── Good files ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("file_path", sorted(GOOD.glob("*.json")))
def test_good_files_have_root_and_paths(file_path: Path):
    text = load_text(file_path)
    locations = create_location_mapping(text)

    # basic sanity
    assert isinstance(locations, dict)
    assert "$" in locations, f"root missing in {file_path.name}"
    assert isinstance(locations["$"], LocationInfo)

    # Ensure no __error__ entry
    assert "$.__error__" not in locations

    # Spot check a few expected paths per file
    if file_path.name == "simple_object.json":
        for p in ("$.user", "$.user.name", "$.user.age", "$.active"):
            assert p in locations
            assert locations[p].kind != "key"

        # keys present with __key__
        for p in (
            "$.user.__key__",
            "$.user.name.__key__",
            "$.user.age.__key__",
            "$.active.__key__",
        ):
            assert p in locations
            assert locations[p].kind == "key"

        # parents chain should be oldest→newest
        assert [p.key for p in locations["$.user.name"].parents] == ["$", "user"]

    if file_path.name == "nested_arrays.json":
        assert "$.items" in locations
        assert "$.items.0" in locations
        assert "$.items.0.tags" in locations
        assert "$.items.0.tags.1" in locations


# ── Bad files ───────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("file_path", sorted(BAD.glob("*.json")))
def test_bad_files_emit_error_entry(file_path: Path):
    text = load_text(file_path)
    locations = create_location_mapping(text)

    # Should NOT raise; should return synthetic error location
    assert "$.__error__" in locations, f"no error entry for {file_path.name}"
    err = locations["$.__error__"]
    assert isinstance(err, LocationInfo)
    assert err.key == "__error__"
    assert err.kind != "key"
    # Basic invariants: 1-based positions and non-decreasing span
    assert err.start_character_number >= 1
    assert err.end_character_number >= err.start_character_number
    assert err.start_line_number >= 1
    assert err.end_line_number >= err.start_line_number
    assert err.start_line_character_number >= 1
    assert err.end_line_character_number >= 1
