from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    """
    Input parameters for web search tool.
    """

    query: str = Field(
        description="Search query to execute",
        min_length=1,
        max_length=1000,
    )
    region: str = Field(
        description="Search region (e.g., us-en, uk-en)",
        pattern=r"^[a-z]{2}-[a-z]{2}$",
    )
    safesearch: str = Field(
        description="Safe search level (off, moderate, strict)",
        pattern=r"^(off|moderate|strict)$",
    )
    max_results: int = Field(
        description="Maximum number of results to return",
        ge=1,
        le=50,
    )

    def __init__(self, **data):
        # Note: This will be called during model validation, so we can't inject config here
        # The config will be used in the WebSearchTool constructor instead
        super().__init__(**data)
