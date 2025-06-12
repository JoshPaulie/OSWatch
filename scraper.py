"""OSRS homepage scraper functionality."""

import logging

import requests
from bs4 import BeautifulSoup

from config import OSRS_HOMEPAGE, REQUEST_TIMEOUT, USER_AGENT

logger = logging.getLogger(__name__)


def get_player_count_text() -> str | None:
    """Get player count text from OSRS homepage."""
    try:
        # Set user agent
        headers = {
            "User-Agent": USER_AGENT,
        }

        # Get homepage text
        response = requests.get(OSRS_HOMEPAGE, timeout=REQUEST_TIMEOUT, headers=headers)
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
