# OS Watch

OSRS world status API. Scrapes player count from RuneScape homepage to determine if game worlds are online and ready.

Acts as an intermediary for other tools to check game world status.

_**Unofficial community API**_

> [!important]
> **OS Watch** is hosted on a free tier of [Render](https://render.com/).
>
> **Cold starts** are unlikely due to me personally using the API to log historic data on my own machine.
>
> Historic data for all would be awesome! But persistent data within Render requires me upgrading the hosting tier. With just me using the service, I'll keep on the current until others express interest.
> 
> If you have a use case that would benefit from 100% availability or historic data, open an issue!

## API Documentation

- **ReDoc**: [https://oswatch.bexli.dev/redoc](https://oswatch.bexli.dev/redoc) - Basic API with code examples (recommended)
- **Swagger UI**: [https://oswatch.bexli.dev/docs](https://oswatch.bexli.dev/docs) - Interactive API documentation with "Try it out"


## Usage (Endpoints)

URL: `https://oswatch.bexli.dev`
- `GET /` - Game status
- `GET /status` - Detailed status (includes cache details)

Game world status is cached for 60s.

## Quick Examples

### Bash (cURL)
```bash
# Basic status check
curl -X GET "https://oswatch.bexli.dev/" \
  -H "Accept: application/json"

# Detailed status with cache info
curl -X GET "https://oswatch.bexli.dev/status" \
  -H "Accept: application/json"
```

### Python

```python
import requests

# Basic status check
response = requests.get("https://oswatch.bexli.dev/")
data = response.json()

print(f"Status: {data['status']}")
print(f"Players: {data['player_count']:,}")
print(f"Message: {data['message']}")
```

#### With TypedDict for Type Safety

```python
import requests
from typing import TypedDict, Literal

# Type definitions for API responses
class GameStatusResponse(TypedDict):
    """Type definition for the root endpoint (/) response."""
    status: Literal["online", "offline", "unknown"]
    player_count: int
    message: str

class DetailedStatusResponse(TypedDict):
    """Type definition for the detailed status endpoint (/status) response."""
    game: str
    online: bool | None
    player_count: int
    homepage_accessible: bool
    source: str
    cache_age_seconds: float
    cache_expires_in_seconds: float
    cache_timestamp: str

# Usage examples with proper typing
def get_game_status() -> GameStatusResponse:
    """Get basic game status with type safety."""
    response = requests.get("https://oswatch.bexli.dev/")
    response.raise_for_status()
    return response.json()

def get_detailed_status() -> DetailedStatusResponse:
    """Get detailed status with cache information and type safety."""
    response = requests.get("https://oswatch.bexli.dev/status")
    response.raise_for_status()
    return response.json()

# Example usage
if __name__ == "__main__":
    # Basic status
    status: GameStatusResponse = get_game_status()
    print(f"Status: {status['status']}")
    print(f"Players: {status['player_count']:,}")
    print(f"Message: {status['message']}")
    
    # Detailed status
    detailed: DetailedStatusResponse = get_detailed_status()
    print(f"Game: {detailed['game']}")
    print(f"Online: {detailed['online']}")
    print(f"Cache age: {detailed['cache_age_seconds']:.1f}s")
```

### JavaScript

```javascript
// Basic status check
fetch('https://oswatch.bexli.dev/')
  .then(response => response.json())
  .then(data => {
    console.log(`Status: ${data.status}`);
    console.log(`Players: ${data.player_count.toLocaleString()}`);
    console.log(`Message: ${data.message}`);
  })
  .catch(error => console.error('Error:', error));
```

### Go

```go
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
)

// GameStatusResponse represents the response from the root endpoint (/)
type GameStatusResponse struct {
    Status      string `json:"status"`
    PlayerCount int    `json:"player_count"`
    Message     string `json:"message"`
}

// DetailedStatusResponse represents the response from the detailed status endpoint (/status)
type DetailedStatusResponse struct {
    Game                    string   `json:"game"`
    Online                  *bool    `json:"online"`
    PlayerCount             int      `json:"player_count"`
    HomepageAccessible      bool     `json:"homepage_accessible"`
    Source                  string   `json:"source"`
    CacheAgeSeconds         float64  `json:"cache_age_seconds"`
    CacheExpiresInSeconds   float64  `json:"cache_expires_in_seconds"`
    CacheTimestamp          string   `json:"cache_timestamp"`
}

// getGameStatus fetches basic game status with proper error handling
func getGameStatus() (*GameStatusResponse, error) {
    resp, err := http.Get("https://oswatch.bexli.dev/")
    if err != nil {
        return nil, fmt.Errorf("failed to fetch status: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("API returned status code: %d", resp.StatusCode)
    }

    var status GameStatusResponse
    if err := json.NewDecoder(resp.Body).Decode(&status); err != nil {
        return nil, fmt.Errorf("failed to decode response: %w", err)
    }

    return &status, nil
}

// getDetailedStatus fetches detailed status with cache information
func getDetailedStatus() (*DetailedStatusResponse, error) {
    resp, err := http.Get("https://oswatch.bexli.dev/status")
    if err != nil {
        return nil, fmt.Errorf("failed to fetch detailed status: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("API returned status code: %d", resp.StatusCode)
    }

    var status DetailedStatusResponse
    if err := json.NewDecoder(resp.Body).Decode(&status); err != nil {
        return nil, fmt.Errorf("failed to decode response: %w", err)
    }

    return &status, nil
}

func main() {
    // Basic status example
    fmt.Println("=== Basic Status ===")
    status, err := getGameStatus()
    if err != nil {
        fmt.Printf("Error fetching status: %v\n", err)
        return
    }

    fmt.Printf("Status: %s\n", status.Status)
    fmt.Printf("Players: %s\n", formatNumber(status.PlayerCount))
    fmt.Printf("Message: %s\n", status.Message)

    // Detailed status example
    fmt.Println("\n=== Detailed Status ===")
    detailed, err := getDetailedStatus()
    if err != nil {
        fmt.Printf("Error fetching detailed status: %v\n", err)
        return
    }

    fmt.Printf("Game: %s\n", detailed.Game)
    if detailed.Online != nil {
        fmt.Printf("Online: %t\n", *detailed.Online)
    } else {
        fmt.Printf("Online: unknown\n")
    }
    fmt.Printf("Players: %s\n", formatNumber(detailed.PlayerCount))
    fmt.Printf("Homepage Accessible: %t\n", detailed.HomepageAccessible)
    fmt.Printf("Cache Age: %.1fs\n", detailed.CacheAgeSeconds)
    fmt.Printf("Cache Expires In: %.1fs\n", detailed.CacheExpiresInSeconds)
}

// formatNumber adds commas to large numbers for better readability
func formatNumber(n int) string {
    if n < 1000 {
        return fmt.Sprintf("%d", n)
    }
    return fmt.Sprintf("%s,%03d", formatNumber(n/1000), n%1000)
}
```
