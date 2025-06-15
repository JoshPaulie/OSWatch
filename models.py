"""Response models for the OSRS World Status API."""

from typing import ClassVar

from pydantic import BaseModel, Field


class GameStatusResponse(BaseModel):
    """
    Response model for the root endpoint.

    Simple status check that returns whether OSRS is online/offline
    along with current player count and a human-readable message.
    """

    status: str = Field(
        ...,
        example="online",
        description="Game status: 'online' if players detected, 'offline' if no players, 'unknown' if homepage inaccessible",
        pattern="^(online|offline|unknown)$",
    )
    player_count: int = Field(
        ...,
        example=138559,
        description="Current number of players online across all OSRS worlds",
        ge=0,
    )
    message: str = Field(
        ...,
        example="OSRS is online with 138,559 players",
        description="Human-readable status message summarizing the current state",
    )

    class Config:
        """Pydantic configuration with example data."""

        json_schema_extra: ClassVar = {
            "examples": [
                {
                    "status": "online",
                    "player_count": 138559,
                    "message": "OSRS is online with 138,559 players",
                },
                {
                    "status": "offline",
                    "player_count": 0,
                    "message": "OSRS is offline",
                },
                {
                    "status": "unknown",
                    "player_count": 0,
                    "message": "OSRS status unknown - homepage inaccessible",
                },
            ],
        }


class DetailedStatusResponse(BaseModel):
    """
    Response model for the detailed status endpoint.

    Comprehensive status information including cache metadata,
    homepage accessibility, and data source information.
    """

    game: str = Field(
        ...,
        example="Old School RuneScape",
        description="Full name of the game being monitored",
    )
    online: bool | None = Field(
        ...,
        example=True,
        description="Whether the game is online (True), offline (False), or unknown (null if homepage inaccessible)",
    )
    player_count: int = Field(
        ...,
        example=138559,
        description="Current number of players online across all OSRS worlds",
        ge=0,
    )
    homepage_accessible: bool = Field(
        ...,
        example=True,
        description="Whether the OSRS homepage is accessible and responding",
    )
    source: str = Field(
        ...,
        example="https://oldschool.runescape.com",
        description="Source URL where status information is retrieved from",
    )
    cache_age_seconds: float = Field(
        ...,
        example=15.2,
        description="How old the cached data is in seconds (0.0 to 60.0)",
        ge=0.0,
        le=60.0,
    )
    cache_expires_in_seconds: float = Field(
        ...,
        example=44.8,
        description="How long until the cache expires in seconds (0.0 to 60.0)",
        ge=0.0,
        le=60.0,
    )
    cache_timestamp: str = Field(
        ...,
        example="2025-06-15T14:30:45.123456+00:00",
        description="ISO 8601 timestamp of when cached data was last fetched (UTC)",
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+00:00$",
    )

    class Config:
        """Pydantic configuration with example data."""

        json_schema_extra: ClassVar = {
            "examples": [
                {
                    "game": "Old School RuneScape",
                    "online": True,
                    "player_count": 138559,
                    "homepage_accessible": True,
                    "source": "https://oldschool.runescape.com",
                    "cache_age_seconds": 15.2,
                    "cache_expires_in_seconds": 44.8,
                    "cache_timestamp": "2025-06-15T14:30:45.123456+00:00",
                },
                {
                    "game": "Old School RuneScape",
                    "online": False,
                    "player_count": 0,
                    "homepage_accessible": True,
                    "source": "https://oldschool.runescape.com",
                    "cache_age_seconds": 8.7,
                    "cache_expires_in_seconds": 51.3,
                    "cache_timestamp": "2025-06-15T14:30:45.123456+00:00",
                },
                {
                    "game": "Old School RuneScape",
                    "online": None,
                    "player_count": 0,
                    "homepage_accessible": False,
                    "source": "https://oldschool.runescape.com",
                    "cache_age_seconds": 0.0,
                    "cache_expires_in_seconds": 60.0,
                    "cache_timestamp": "2025-06-15T14:30:45.123456+00:00",
                },
            ],
        }
