# OSWatch

OSRS world status API. Scrapes player count from RuneScape homepage to determine if game worlds are online and ready.

Acts as an intermediary for other tools to check game world status.

> [!important]
> The app is hosted on a free tier, so it powers down after idling for some time. You may experience a "cold start" when trying to access the API, but is unlikely.
>
> If you're using the API and need it available 24/7, open an issue with your usecase. I'd be happy to upgrade to an "always on" tier, if there's a need from the community.

## Usage (Endpoints)
URL: `https://oswatch.bexli.dev`
- `GET /` - Game status
- `GET /status` - Detailed status (includes cache details)

Game world status is cached for 60s.

[Read the docs for more](https://oswatch.bexli.dev/docs/)
