# 002 — ESPN blocks cloud IPs (GitHub Actions), add hockeystats.com fallback

**Created:** 2026-05-10

## Problem

ESPN returns HTTP 403 Forbidden for requests from cloud/datacenter IPs, which includes GitHub Actions runners and the VPS (OVH). This caused the automated CI workflow to produce noise commits from cached fallback data — and after fixing that (issue #001), the dashboard stopped updating entirely.

Residential IPs (ser5 at 94.157.122.90) work fine against ESPN.

## Root cause

ESPN uses IP-based bot detection that blocks known cloud provider IP ranges (Azure, OVH, etc.). The same `parse-odds.py` script works from ser5 (residential) but fails on GitHub Actions runners and VPS.

## Solution

Added hockeystats.com as a fallback data source. It uses JSON-LD structured data (`<script type="application/ld+json">` blocks) that:

- Works from cloud IPs (no 403 blocking)
- Contains Stanley Cup win probabilities as structured data (`SportsTeam` type with `additionalProperty`)
- Is more stable than HTML table parsing (structured schema.org data)

The fallback chain is now: ESPN → hockeystats.com → cached JSON.

A hockeystats scrape counts as "live" data (exit code 0), so the CI workflow commits and deploys successfully.

## Testing

| Machine | ESPN | hockeystats | Exit code |
|---------|------|-------------|-----------|
| ser5 (residential) | ✅ 7 teams | Not needed | 0 |
| VPS (OVH) | ❌ 403 | ✅ 7 teams | 0 |
| GitHub Actions (Azure) | ❌ 403 | ✅ 7 teams (expected) | 0 |
