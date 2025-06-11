# OSWatch

OSRS world status API. Scrapes player count from RuneScape homepage to determine if game worlds are online and ready.

Acts as an intermediary for other tools to check game world status.

> [!important]
> The app is hosted on a free tier, so it powers down after idling for some time. You may experience a "cold start" when trying to access the API.
> 
> It'll remain this way until I (or someone else) has a project ready for it. I'm considering creating a separate notification system for the API.
>
> If you're interested in using it in your project, open a ticket with your usecase. I'd be happy to bump it to an "always on" tier if the community could use it.

## Usage (Endpoints)
- `GET /` - Game status
- `GET /status` - Detailed status (includes cache details)

Game world status is cached for 60s.

[Read the docs for more](https://oswatch.onrender.com/docs#/)
