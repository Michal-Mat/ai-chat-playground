from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """
    Search request parameters.
    """

    query: str = Field(
        description="Search query string",
        min_length=1,
        max_length=1000,
    )
    region: str = Field(
        default="us-en",
        description="Search region (e.g., us-en, uk-en)",
        pattern=r"^[a-z]{2}-[a-z]{2}$",
    )
    safesearch: str = Field(
        default="moderate",
        description="Safe search level",
        pattern=r"^(off|moderate|strict)$",
    )
    max_results: int = Field(
        description="Maximum number of results to return",
        default=10,
        ge=1,
        le=50,
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Clean and validate search query."""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Query cannot be empty")
        if len(cleaned) > 1000:
            raise ValueError("Query too long (max 1000 characters)")
        return cleaned

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            # Add any custom JSON encoders if needed
        }
