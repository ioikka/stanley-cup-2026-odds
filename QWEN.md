# Stanley Cup 2026 Odds Dashboard

## Project Overview

A live Stanley Cup futures odds tracker that scrapes ESPN for NHL championship odds, tiers teams by win probability (favorite / contender / longshot), and serves a polished HTML dashboard with webhook-based auto-refresh. Deployed as a GitHub Pages static site with automated data updates via GitHub Actions.

**Technologies:** Python 3 (stdlib only — no external dependencies), HTML/CSS/JS, GitHub Actions, GitHub Pages

**Live dashboard:** https://ioikka.github.io/stanley-cup-2026-odds/stanley-cup-odds.html

## Key Files

| File | Purpose |
|------|---------|
| `parse-odds.py` | ESPN scraper — fetches futures odds + playoff bracket, computes win probabilities, assigns tiers, downloads team logos, writes `data/odds.json` |
| `static-server.py` | Local HTTP server on `:8888` with `/webhook/refresh` (triggers re-scrape) and `/webhook/status` endpoints |
| `stanley-cup-odds.html` | Self-contained dashboard UI (424 lines, no external JS/CSS deps beyond Google Fonts) |
| `data/odds.json` | Scraped odds data (output artifact — not manually edited) |
| `.github/workflows/refresh-odds.yaml` | Scheduled GitHub Action (every 2 hours) that runs `parse-odds.py` and commits updated data |
| `update-odds.bat` | Windows convenience wrapper to run `parse-odds.py` |
| `logos/` | NHL team SVG logos from NHL CDN (git-ignored, re-downloadable) |

## Building and Running

### Scrape odds from ESPN
```bash
python parse-odds.py
```
Outputs to `data/odds.json` with team odds, probabilities, tier assignments, and eliminated teams.

### Serve the local dashboard
```bash
python static-server.py
# → http://localhost:8888
```

### Trigger a live re-scrape (without restarting the server)
```bash
curl -X POST http://localhost:8888/webhook/refresh
```

### Check server/data status
```bash
curl http://localhost:8888/webhook/status
```

## Data Pipeline

1. **Scrape** — `parse-odds.py` fetches ESPN NHL Futures page, extracts embedded JSON containing Stanley Cup winner odds
2. **Parse** — bracket-counting JSON extraction from HTML, American odds → win probability conversion, tier assignment (`fav` ≥9%, `con` ≥3%, `horse` <3%)
3. **Enhance** — fetches ESPN Playoff Bracket to update live statuses (e.g., "Adv - Swept Kings 4-0")
4. **Fallback** — if fewer than 10 teams are scraped, falls back to cached `data/odds.json`
5. **Logos** — downloads team SVG logos from `assets.nhle.com` to `logos/`
6. **Save** — writes structured JSON with metadata, teamColors, and teams arrays

## API Endpoints (local server)

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Dashboard HTML |
| `GET` | `/webhook/status` | Server + data status JSON |
| `POST` | `/webhook/refresh` | Trigger fresh ESPN scrape |

All endpoints include CORS headers (`Access-Control-Allow-Origin: *`).

## Automated Updates

GitHub Actions runs `refresh-odds.yaml` on a **2-hour schedule** (`cron: "0 */2 * * *"`). It checks out the repo, runs `parse-odds.py`, and auto-commits any changes to `data/odds.json`. Can also be triggered manually via `workflow_dispatch`.

## Coding Conventions

- **No external Python dependencies** — uses only stdlib (`urllib`, `json`, `http.server`, `subprocess`)
- **Team data** hardcoded in `ABBR_INFO` dict in `parse-odds.py` (16 tracked teams with full names and color schemes)
- **Logos are git-ignored** — always re-downloaded from NHL CDN by the parser
- **Probability calculation** uses standard American odds formula: positive → `100/(odds+100)*100`, negative → `abs(odds)/(abs(odds)+100)*100`
- **Tier thresholds:** `fav` (≥9%), `con` (≥3%), `horse` (<3%)
- HTML dashboard is self-contained (inline CSS, no JS framework)

## Issue Tracking (`_issues/`)

Issues are tracked as Markdown files in the `_issues/` directory instead of an external issue tracker.

### Naming Convention

```
_NNN-YYYY-MM-DD-short-descriptive-title_STATUS.md
```

| Component | Format | Separator within group | Example |
|-----------|--------|------------------------|---------|
| Sequence number | 3-digit zero-padded | — | `001` |
| Date | YYYY-MM-DD | hyphens | `2026-05-10` |
| Title slug | kebab-case words | hyphens | `noise-commits-from-cached-fallback` |
| Status | uppercase | — | `OPEN`, `INPROGRESS`, `DONE` |

- **Groups** (number, date, title, status) are separated by **underscores** (`_`)
- **Elements within a group** are separated by **hyphens** (`-`)

**Example:** `001_2026-05-10-noise-commits-from-cached-fallback_OPEN.md`

### Rules

- Sequence numbers are sequential, gap-free, starting at `001`
- When an issue status changes, **rename the file** to update the status suffix
- The first line of each issue file should be `# NNN — Title` with `**Created:** YYYY-MM-DD` on the next line

### Status Values

| Status | Meaning |
|--------|---------|
| `OPEN` | Identified, not yet worked on |
| `INPROGRESS` | Currently being addressed |
| `DONE` | Resolved and closed |

## Git Ignore

- `logos/` — regenerated by parser
- `__pycache__/`, `*.pyc`, `*.pyo` — Python bytecode
