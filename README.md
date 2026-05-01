# Stanley Cup 2026 Odds Dashboard

Live Stanley Cup futures odds tracker — scrapes ESPN, tiers teams by win probability, and serves a polished dashboard with webhook-based auto-refresh.

## Quick Start

```bash
# Scrape odds from ESPN → data/odds.json
python parse-odds.py

# Serve the dashboard
python static-server.py
# → http://localhost:8888
```

## How It Works

1. **Scrape** — `parse-odds.py` hits ESPN Futures for Stanley Cup winner odds and ESPN Playoff Bracket for live status
2. **Parse** — extracts team odds, win probability, tier assignment (favorite / contender / longshot)
3. **Serve** — `static-server.py` delivers the HTML dashboard + JSON API at `localhost:8888`
4. **Refresh** — `POST /webhook/refresh` triggers a live re-scrape without restarting the server

**Data sources:**
- ESPN NHL Futures (primary)
- ESPN Playoff Bracket (secondary — status updates)
- NHL CDN (team SVG logos → `logos/`)

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Dashboard HTML |
| `GET` | `/webhook/status` | Server + data status |
| `POST` | `/webhook/refresh` | Trigger fresh ESPN scrape |

All endpoints include CORS headers.

## Auto-Refresh

GitHub Actions (`refresh-odds.yaml`) runs on a schedule to keep `data/odds.json` current.

**🔗 Live dashboard:** https://ioikka.github.io/stanley-cup-2026-odds/

## File Structure

| Path | Purpose |
|------|---------|
| `stanley-cup-odds.html` | Main dashboard UI |
| `parse-odds.py` | ESPN scraper, probability tiers, `data/odds.json` pipeline |
| `static-server.py` | Local server on `:8888` |
| `.github/workflows/refresh-odds.yaml` | Scheduled scrape + push |
| `data/odds.json` | Scraped odds data |
| `logos/` | NHL team SVG logos |

## License

MIT
