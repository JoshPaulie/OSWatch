"""Cache management for OSRS status data."""

import logging
import time
from typing import TypedDict

from config import CACHE_DURATION
from scraper import get_player_count, get_player_count_text

logger = logging.getLogger(__name__)

# Just playing around, not sure how much this improves readability.
IsOnline = bool
PlayerCount = int
IsHomePageAccessible = bool
GameStatus = tuple[IsOnline | None, PlayerCount, IsHomePageAccessible]


class CacheData(TypedDict):
    """Type definition for cache storage."""

    data: GameStatus | None
    timestamp: float


_cache: CacheData = {
    "data": None,
    "timestamp": 0,
}


def is_game_online() -> GameStatus:
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


def get_cache_info() -> dict:
    """Get cache information for status endpoint."""
    cache_age = time.time() - _cache["timestamp"] if _cache["data"] else 0
    return {
        "cache_age_seconds": round(cache_age, 1),
        "cache_expires_in_seconds": max(0, round(CACHE_DURATION - cache_age, 1)),
        "timestamp": _cache["timestamp"],
    }
