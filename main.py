"""OSRS World Status API - Monitor Old School RuneScape server status."""

import datetime as dt
import logging
import time

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# --- Configure logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Response Models ---
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


app = FastAPI(
    title="OSRS World Status API",
    description="Check if Old School RuneScape game worlds are online by monitoring player count. "
    "Responses are cached for 1 minute to reduce load on OSRS servers. "
    "To be used as an intermediary for your automation.",
    version="1.0.2",
)

OSRS_HOMEPAGE = "https://oldschool.runescape.com"
CACHE_DURATION = 60  # Seconds

# --- Cache storage ---
_cache = {
    "data": None,
    "timestamp": 0,
}


# --- Helpers ---
def get_player_count_text() -> str | None:
    """Get player count text from OSRS homepage."""
    try:
        # Set user agent
        headers = {
            "User-Agent": "OSRS-Status-Monitor/1.0 (https://github.com/JoshPaulie/OSWatch) - Monitoring server status with 60s cache",
        }

        # Get homepage text
        response = requests.get(OSRS_HOMEPAGE, timeout=30, headers=headers)
        response.raise_for_status()

        # Parse text
        soup = BeautifulSoup(response.content, "html.parser")

        # Find target tag
        player_count_element = soup.find("p", class_="player-count")
        if player_count_element:
            return player_count_element.text

    except requests.RequestException:
        logger.exception("Error fetching player count")
        return None

    else:
        return None


def get_player_count(player_count_text: str) -> int:
    """Parse player count from text."""
    if not player_count_text:
        return 0

    digits = "".join([num for num in player_count_text if num.isdigit()])
    return int(digits) if digits else 0


def is_game_online() -> tuple[bool | None, int, bool]:
    """
    Check if the game is online based on player count with caching.

    Returns:
        tuple: (is_online, player_count, homepage_accessible)
        - is_online: True if online, False if offline, None if unknown
        - player_count: Number of players (0 if unknown)
        - homepage_accessible: True if OSRS homepage was accessible

    """
    current_time = time.time()

    # Check if we have cached data that's still valid
    if (
        _cache["data"] is not None
        and current_time - _cache["timestamp"] < CACHE_DURATION
    ):
        logger.info("Serving cached data")
        return _cache["data"]

    # Cache expired or doesn't exist, fetch new data
    logger.info("Fetching fresh data from OSRS homepage")
    text = get_player_count_text()

    if text is None:
        # Homepage is inaccessible
        result = (None, 0, False)
    else:
        # Homepage is accessible, determine status
        player_count = get_player_count(text)
        is_online = player_count > 0
        result = (is_online, player_count, True)

    # Cache the result
    _cache["data"] = result
    _cache["timestamp"] = current_time

    return result


# --- API Endpoints ---
@app.get("/")
async def root() -> GameStatusResponse:
    """Get OSRS world status."""
    is_online, player_count, homepage_accessible = is_game_online()

    if not homepage_accessible:
        raise HTTPException(
            status_code=503,
            detail="OSRS homepage is currently inaccessible - status unknown",
        )

    return GameStatusResponse(
        status="online" if is_online else "offline",
        player_count=player_count,
        message=f"OSRS is {'online' if is_online else 'offline'}"
        + (f" with {player_count:,} players" if is_online else ""),
    )


@app.get("/status")
async def status() -> DetailedStatusResponse:
    """Detailed status endpoint."""
    is_online, player_count, homepage_accessible = is_game_online()
    cache_age = time.time() - _cache["timestamp"] if _cache["data"] else 0

    # Convert cache timestamp to UTC format
    cache_timestamp = (
        dt.datetime.fromtimestamp(_cache["timestamp"], dt.UTC).isoformat()
        if _cache["data"]
        else dt.datetime.now(dt.UTC).isoformat()
    )

    return DetailedStatusResponse(
        game="Old School RuneScape",
        online=is_online,
        player_count=player_count,
        homepage_accessible=homepage_accessible,
        source=OSRS_HOMEPAGE,
        cache_age_seconds=round(cache_age, 1),
        cache_expires_in_seconds=max(0, round(CACHE_DURATION - cache_age, 1)),
        cache_timestamp=cache_timestamp,
    )


def main() -> None:
    """CLI functionality."""
    is_online, player_count, homepage_accessible = is_game_online()

    if not homepage_accessible:
        print("OSRS homepage is inaccessible - status unknown.")
    elif is_online:
        print(f"OSRS is online with {player_count:,} players")
    else:
        print("OSRS is offline.")


if __name__ == "__main__":
    main()
