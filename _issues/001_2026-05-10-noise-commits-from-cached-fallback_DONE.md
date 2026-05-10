# 001 — Noise Commits from Cached Fallback

**Created:** 2026-05-10

## Problem

The GitHub Actions workflow produces commits with no real data change. ESPN scraping fails consistently on the runner, triggering the cached fallback. The only difference between commits is the `lastUpdated` timestamp in `metadata`.

## Evidence

```
git diff HEAD~3 HEAD -- data/odds.json
```

Shows only `lastUpdated` changed and `sources` switched from `["espn", "espn_bracket"]` to `["cached"]`.

## Root Cause

1. `parse-odds.py` fails to fetch ESPN (likely rate-limiting / bot-blocking on GitHub Actions network)
2. Fallback path loads cached `data/odds.json`, updates the timestamp, and re-saves
3. `refresh-odds.yaml` commits any staged change — including the timestamp bump

## Proposed Fix

**Option A — Skip commit if fallback was used:** Only commit when `sources` includes `"espn"` (real scrape succeeded).

**Option B — Diff teams array only:** Ignore `metadata.lastUpdated` when deciding whether to commit.

**Option C — Both:** Skip commit unless a live scrape succeeded AND team data actually changed.

Recommendation: **Option C** — most robust, prevents all noise.
