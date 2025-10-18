from typing import Literal

from pydantic import BaseModel, Field

# ── Types ───────────────────────────────────────────────────────────────────────

Kind = Literal["key", "object", "list", "null", "string", "boolean", "number"]


class LocationInfo(BaseModel):
    """
    Represents the location information for a JSON element in the source text.

    This class contains precise positioning data including character offsets,
    line/column numbers, and hierarchical relationships within the JSON structure.

    Attributes:
        parents: List of parent LocationInfo objects from oldest to most recent
        key: The name/key of this element
        kind: The type of JSON element ("key", "object", "list", "null", "string", "boolean", "number")
        start_character_number: 1-based character position where element starts
        start_line_number: 1-based line number where element starts
        start_line_character_number: 1-based column number where element starts
        end_character_number: 1-based character position where element ends
        end_line_number: 1-based line number where element ends
        end_line_character_number: 1-based column number where element ends

    Properties:
        level: The nesting depth of this element (number of parents)
    """

    parents: list["LocationInfo"] = Field(
        default_factory=list,
        description="The parents from oldest first to most recent last",
    )
    key: str = Field(..., description="The name of this object")
    kind: Kind = Field(..., description="The kind of object: key or value")

    # 1-based absolute character offsets and line/column positions
    start_character_number: int = Field(
        ..., ge=1, description="Character number within the full text"
    )
    start_line_number: int = Field(
        ..., ge=1, description="Line number within the full text"
    )
    start_line_character_number: int = Field(
        ..., ge=1, description="Character number within the start line"
    )

    end_character_number: int = Field(
        ..., ge=1, description="Character number within the full text"
    )
    end_line_number: int = Field(
        ..., ge=1, description="Line number within the full text"
    )
    end_line_character_number: int = Field(
        ..., ge=1, description="Character number within the end line"
    )

    @property
    def level(self) -> int:
        """
        Get the nesting level of this element.

        Returns:
            Number of parent elements (nesting depth)
        """
        return len(self.parents)

    def __hash__(self) -> int:
        """
        Make LocationInfo hashable for use as dictionary keys.

        Returns:
            Hash value based on the unique characteristics of this location
        """
        # Use a combination of key characteristics that should be unique
        return hash(
            (
                self.key,
                self.kind,
                self.start_character_number,
                self.end_character_number,
                self.start_line_number,
                self.start_line_character_number,
                self.end_line_number,
                self.end_line_character_number,
                tuple(
                    p.key for p in self.parents
                ),  # Convert parents to tuple for hashing
            )
        )

    def __eq__(self, other: object) -> bool:
        """
        Check equality between LocationInfo objects.

        Args:
            other: Another object to compare with

        Returns:
            True if the objects represent the same location
        """
        if not isinstance(other, LocationInfo):
            return False

        return (
            self.key == other.key
            and self.kind == other.kind
            and self.start_character_number == other.start_character_number
            and self.end_character_number == other.end_character_number
            and self.start_line_number == other.start_line_number
            and self.start_line_character_number == other.start_line_character_number
            and self.end_line_number == other.end_line_number
            and self.end_line_character_number == other.end_line_character_number
            and self.parents == other.parents
        )
