from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class SearchResult(BaseModel):
    """
    Individual search result from web search.
    """

    title: str = Field(
        description="Title of the search result",
        min_length=1,
    )
    url: str = Field(
        description="URL of the search result",
        min_length=1,
    )
    snippet: str = Field(
        description="Text snippet/description of the result",
        default="",
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL is properly formatted."""
        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
            return v
        except Exception as e:
            raise ValueError(f"Invalid URL: {e}") from e

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Clean and validate title."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned

    @field_validator("snippet")
    @classmethod
    def validate_snippet(cls, v: str) -> str:
        """Clean snippet text."""
        return v.strip()

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add any custom JSON encoders if needed
        }
