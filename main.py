"""OSRS World Status API - Monitor Old School RuneScape server status."""

import datetime as dt
import logging

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

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


def custom_openapi() -> dict:
    """Generate custom OpenAPI schema with multi-language code examples."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add code examples for the root endpoint
    if "/" in openapi_schema["paths"]:
        openapi_schema["paths"]["/"]["get"]["x-code-samples"] = [
            {
                "lang": "bash",
                "label": "cURL",
                "source": 'curl -X GET "https://oswatch.bexli.dev/" \\\n  -H "Accept: application/json"',
            },
            {
                "lang": "python",
                "label": "Python (requests)",
                "source": 'import requests\n\nresponse = requests.get("https://oswatch.bexli.dev/")\ndata = response.json()\n\nprint(f"Status: {data[\'status\']}")\nprint(f"Players: {data[\'player_count\']:,}")\nprint(f"Message: {data[\'message\']}")',
            },
            {
                "lang": "javascript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://oswatch.bexli.dev/')\n  .then(response => response.json())\n  .then(data => {\n    console.log(`Status: ${data.status}`);\n    console.log(`Players: ${data.player_count.toLocaleString()}`);\n    console.log(`Message: ${data.message}`);\n  })\n  .catch(error => console.error('Error:', error));",
            },
            {
                "lang": "go",
                "label": "Go",
                "source": 'package main\n\nimport (\n    "encoding/json"\n    "fmt"\n    "net/http"\n)\n\ntype GameStatus struct {\n    Status      string `json:"status"`\n    PlayerCount int    `json:"player_count"`\n    Message     string `json:"message"`\n}\n\nfunc main() {\n    resp, err := http.Get("https://oswatch.bexli.dev/")\n    if err != nil {\n        panic(err)\n    }\n    defer resp.Body.Close()\n\n    var status GameStatus\n    json.NewDecoder(resp.Body).Decode(&status)\n\n    fmt.Printf("Status: %s\\n", status.Status)\n    fmt.Printf("Players: %d\\n", status.PlayerCount)\n    fmt.Printf("Message: %s\\n", status.Message)\n}',
            },
        ]

    # Add code examples for the status endpoint
    if "/status" in openapi_schema["paths"]:
        openapi_schema["paths"]["/status"]["get"]["x-code-samples"] = [
            {
                "lang": "bash",
                "label": "cURL",
                "source": 'curl -X GET "https://oswatch.bexli.dev/status" \\\n  -H "Accept: application/json"',
            },
            {
                "lang": "python",
                "label": "Python (requests)",
                "source": 'import requests\nfrom datetime import datetime\n\nresponse = requests.get("https://oswatch.bexli.dev/status")\ndata = response.json()\n\nprint(f"Game: {data[\'game\']}")\nprint(f"Online: {data[\'online\']}")\nprint(f"Players: {data[\'player_count\']:,}")\nprint(f"Homepage accessible: {data[\'homepage_accessible\']}")\nprint(f"Cache age: {data[\'cache_age_seconds\']:.1f}s")\nprint(f"Cache expires in: {data[\'cache_expires_in_seconds\']:.1f}s")\nprint(f"Last updated: {data[\'cache_timestamp\']}")',
            },
            {
                "lang": "javascript",
                "label": "JavaScript (fetch)",
                "source": "fetch('https://oswatch.bexli.dev/status')\n  .then(response => response.json())\n  .then(data => {\n    console.log(`Game: ${data.game}`);\n    console.log(`Online: ${data.online}`);\n    console.log(`Players: ${data.player_count.toLocaleString()}`);\n    console.log(`Homepage accessible: ${data.homepage_accessible}`);\n    console.log(`Cache age: ${data.cache_age_seconds.toFixed(1)}s`);\n    console.log(`Cache expires in: ${data.cache_expires_in_seconds.toFixed(1)}s`);\n    console.log(`Last updated: ${data.cache_timestamp}`);\n  })\n  .catch(error => console.error('Error:', error));",
            },
            {
                "lang": "go",
                "label": "Go",
                "source": 'package main\n\nimport (\n    "encoding/json"\n    "fmt"\n    "net/http"\n)\n\ntype DetailedStatus struct {\n    Game                    string  `json:"game"`\n    Online                  *bool   `json:"online"`\n    PlayerCount            int     `json:"player_count"`\n    HomepageAccessible     bool    `json:"homepage_accessible"`\n    Source                 string  `json:"source"`\n    CacheAgeSeconds        float64 `json:"cache_age_seconds"`\n    CacheExpiresInSeconds  float64 `json:"cache_expires_in_seconds"`\n    CacheTimestamp         string  `json:"cache_timestamp"`\n}\n\nfunc main() {\n    resp, err := http.Get("https://oswatch.bexli.dev/status")\n    if err != nil {\n        panic(err)\n    }\n    defer resp.Body.Close()\n\n    var status DetailedStatus\n    json.NewDecoder(resp.Body).Decode(&status)\n\n    fmt.Printf("Game: %s\\n", status.Game)\n    if status.Online != nil {\n        fmt.Printf("Online: %t\\n", *status.Online)\n    } else {\n        fmt.Println("Online: unknown")\n    }\n    fmt.Printf("Players: %d\\n", status.PlayerCount)\n    fmt.Printf("Homepage accessible: %t\\n", status.HomepageAccessible)\n    fmt.Printf("Cache age: %.1fs\\n", status.CacheAgeSeconds)\n    fmt.Printf("Cache expires in: %.1fs\\n", status.CacheExpiresInSeconds)\n    fmt.Printf("Last updated: %s\\n", status.CacheTimestamp)\n}',
            },
        ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set the custom OpenAPI function
app.openapi = custom_openapi


# --- API Endpoints ---
@app.get(
    "/",
    responses={
        200: {
            "description": "Successful response with game status",
            "content": {
                "application/json": {
                    "examples": {
                        "online": {
                            "summary": "Game is online",
                            "value": {
                                "status": "online",
                                "player_count": 144644,
                                "message": "OSRS is online with 144,644 players",
                            },
                        },
                        "offline": {
                            "summary": "Game is offline",
                            "value": {
                                "status": "offline",
                                "player_count": 0,
                                "message": "OSRS is offline",
                            },
                        },
                        "unknown": {
                            "summary": "Game status unknown (homepage inaccessible)",
                            "value": {
                                "status": "unknown",
                                "player_count": 0,
                                "message": "OSRS status unknown - homepage inaccessible",
                            },
                        },
                    },
                },
            },
        },
    },
)
async def root() -> GameStatusResponse:
    """Get OSRS world status."""
    is_online, player_count, homepage_accessible = is_game_online()

    if not homepage_accessible:
        return GameStatusResponse(
            status="unknown",
            player_count=0,
            message="OSRS status unknown - homepage inaccessible",
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
