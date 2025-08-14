from pydantic import BaseModel, Field


class WebSearchOutput(BaseModel):
    """
    Output from web search tool.
    """

    success: bool = Field(
        description="Whether the search was successful",
    )
    query: str = Field(
        description="Original search query",
    )
    results: list[dict[str, str]] = Field(
        description="List of search results with title, url, and snippet",
        default_factory=list,
    )
    total_results: int = Field(
        description="Total number of results found",
        default=0,
    )
    search_time_ms: float = Field(
        description="Search execution time in milliseconds",
        default=0.0,
    )
    error_message: str = Field(
        description="Error message if search failed",
        default="",
    )
    source: str = Field(
        description="Search source/provider",
        default="duckduckgo",
    )
