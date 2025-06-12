"""OSRS World Status API - Monitor Old School RuneScape server status."""

import datetime as dt
import logging

from fastapi import FastAPI, HTTPException

from cache import get_cache_info, is_game_online
from config import OSRS_HOMEPAGE
from models import DetailedStatusResponse, GameStatusResponse

# --- Configure logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI app ---
app = FastAPI(
    title="OSRS World Status API",
    description="Check if Old School RuneScape game worlds are online by monitoring player count. "
    "Responses are cached for 1 minute to reduce load on OSRS servers. "
    "To be used as an intermediary for your automation.",
    version="1.0.2",
)


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
    cache_info = get_cache_info()

    # Convert cache timestamp to UTC format
    cache_timestamp = (
        dt.datetime.fromtimestamp(cache_info["timestamp"], dt.UTC).isoformat()
        if cache_info["timestamp"] > 0
        else dt.datetime.now(dt.UTC).isoformat()
    )

    return DetailedStatusResponse(
        game="Old School RuneScape",
        online=is_online,
        player_count=player_count,
        homepage_accessible=homepage_accessible,
        source=OSRS_HOMEPAGE,
        cache_age_seconds=cache_info["cache_age_seconds"],
        cache_expires_in_seconds=cache_info["cache_expires_in_seconds"],
        cache_timestamp=cache_timestamp,
    )
