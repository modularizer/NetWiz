import json

from netwiz_backend.json_tracker.helpers import _line_length_at
from netwiz_backend.json_tracker.types import LocationInfo


class TrackedJSONDecodeError(json.JSONDecodeError):
    """
    Enhanced JSON decode error with precise location information.

    Extends the standard JSONDecodeError to include LocationInfo for better
    error reporting and debugging. Provides methods to get context snippets
    and formatted error messages.

    Attributes:
        error_loc: LocationInfo object with precise error location
    """

    def __init__(
        self,
        error_loc: LocationInfo,
        json_text: str,
        message: str = "JSON syntax error",
    ) -> None:
        """
        Initialize TrackedJSONDecodeError.

        Args:
            error_loc: LocationInfo with error position details
            json_text: The original JSON text that failed to parse
            message: Error message describing the problem
        """
        # JSONDecodeError takes (msg, doc, pos) with pos 0-based
        pos0 = max(0, error_loc.start_character_number - 1)
        super().__init__(message, json_text, pos0)
        self.error_loc = error_loc  # full structured position data

    # Pretty context
    def snippet(self, radius: int = 40) -> str:
        """
        Get a snippet of text around the error location.

        Args:
            radius: Number of characters to include before and after the error

        Returns:
            Text snippet with newlines escaped
        """
        start = max(0, self.pos - radius)
        end = min(len(self.doc), self.pos + radius)
        return self.doc[start:end].replace("\n", "\\n")

    def __str__(self) -> str:
        """
        Get a formatted error message with location and context.

        Returns:
            Human-readable error message with line/column info and context
        """
        # lineno/colno are provided by base class; convert char index to 1-based for humans
        return (
            f"{self.msg} at line {self.lineno}, column {self.colno} "
            f"(char {self.pos + 1}). Context: …{self.snippet()}…"
        )

    # Convenience: wrap stdlib errors (build a minimal LocationInfo)
    @classmethod
    def from_stdlib_error(
        cls, e: json.JSONDecodeError, json_text: str
    ) -> "TrackedJSONDecodeError":
        """
        Create TrackedJSONDecodeError from a standard JSONDecodeError.

        Args:
            e: Standard JSONDecodeError to convert
            json_text: The original JSON text

        Returns:
            TrackedJSONDecodeError with enhanced location information
        """
        # minimal LocationInfo centered at the error site
        try:
            # _line_length_at exists in your file already
            end_col = min(e.colno + 1, max(1, _line_length_at(json_text, e.lineno)))
        except Exception:
            end_col = e.colno + 1

        loc = LocationInfo(
            parents=[],  # leave empty; callers can fill if desired
            key="__error__",
            kind="string",  # not a real JSON value; placeholder is fine
            start_character_number=e.pos + 1,
            start_line_number=e.lineno,
            start_line_character_number=e.colno,
            end_character_number=min(len(json_text), e.pos + 1) + 1
            if len(json_text)
            else 1,
            end_line_number=e.lineno,
            end_line_character_number=end_col,
        )
        return cls(loc, json_text, e.msg)

    # Convenience: construct from an existing LocationInfo (your synthesized one)
    @classmethod
    def from_location(
        cls, loc: LocationInfo, json_text: str, message: str = "JSON syntax error"
    ) -> "TrackedJSONDecodeError":
        """
        Create TrackedJSONDecodeError from an existing LocationInfo.

        Args:
            loc: LocationInfo with error position details
            json_text: The original JSON text
            message: Error message describing the problem

        Returns:
            TrackedJSONDecodeError instance
        """
        return cls(loc, json_text, message)
