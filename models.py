"""Response models for the OSRS World Status API."""

from pydantic import BaseModel, Field


class GameStatusResponse(BaseModel):
    """Response model for the root endpoint."""

    status: str = Field(
        ...,
        example="online",
        description="Game status: 'online', 'offline', or 'unknown'",
    )
    player_count: int = Field(
        ...,
        example=138559,
        description="Current number of players online",
    )
    message: str = Field(
        ...,
        example="OSRS is online with 138,559 players",
        description="Human-readable status message",
    )


class DetailedStatusResponse(BaseModel):
    """Response model for the detailed status endpoint."""

    game: str = Field(..., example="Old School RuneScape", description="Game name")
    online: bool | None = Field(
        ...,
        example=True,
        description="Whether the game is online (null if unknown)",
    )
    player_count: int = Field(
        ...,
        example=138559,
        description="Current number of players online",
    )
    homepage_accessible: bool = Field(
        ...,
        example=True,
        description="Whether the OSRS homepage is accessible",
    )
    source: str = Field(
        ...,
        example="https://oldschool.runescape.com",
        description="Source URL for status information",
    )
    cache_age_seconds: float = Field(
        ...,
        example=15.2,
        description="How old the cached data is in seconds",
    )
    cache_expires_in_seconds: float = Field(
        ...,
        example=44.8,
        description="How long until the cache expires in seconds",
    )
    cache_timestamp: str = Field(
        ...,
        example="2025-06-11T23:36:14.237361+00:00",
        description="Timestamp of when cached data was last fetched (UTC)",
    )
