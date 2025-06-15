# OSWatch

OSRS world status API. Scrapes player count from RuneScape homepage to determine if game worlds are online and ready.

Acts as an intermediary for other tools to check game world status.

> [!important]
> The app is hosted on a free tier, so it powers down after idling for some time. You may experience a "cold start" when trying to access the API, but is unlikely.
>
> If you're using the API and need it available 24/7, open an issue with your usecase. I'd be happy to upgrade to an "always on" tier, if there's a need from the community.

## API Documentation

- **Swagger UI**: [https://oswatch.bexli.dev/docs](https://oswatch.bexli.dev/docs) - Interactive API documentation with "Try it out" functionality
- **ReDoc**: [https://oswatch.bexli.dev/redoc](https://oswatch.bexli.dev/redoc) - Clean, responsive API documentation (recommended)


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

type GameStatus struct {
    Status      string `json:"status"`
    PlayerCount int    `json:"player_count"`
    Message     string `json:"message"`
}

func main() {
    resp, err := http.Get("https://oswatch.bexli.dev/")
    if err != nil {
        panic(err)
    }
    defer resp.Body.Close()

    var status GameStatus
    json.NewDecoder(resp.Body).Decode(&status)

    fmt.Printf("Status: %s\n", status.Status)
    fmt.Printf("Players: %d\n", status.PlayerCount)
    fmt.Printf("Message: %s\n", status.Message)
}
```

--- 

[Read the complete interactive docs](https://oswatch.bexli.dev/redoc)
