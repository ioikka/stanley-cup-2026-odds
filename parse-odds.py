import urllib.request
import urllib.parse
import json
import os
import re
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "odds.json")
LOGOS_DIR = os.path.join(BASE_DIR, "logos")

# Abbr -> known team info
ABBR_INFO = {
    "COL": {"full": "Colorado Avalanche", "colors": {"bg": "#6F263D", "accent": "#236192"}},
    "CAR": {"full": "Carolina Hurricanes", "colors": {"bg": "#CC0000", "accent": "#000000"}},
    "TB":  {"full": "Tampa Bay Lightning", "colors": {"bg": "#002868", "accent": "#005A90"}},
    "VGK": {"full": "Vegas Golden Knights", "colors": {"bg": "#B4975A", "accent": "#333F4C"}},
    "BUF": {"full": "Buffalo Sabres", "colors": {"bg": "#274488", "accent": "#FFB81C"}},
    "DAL": {"full": "Dallas Stars", "colors": {"bg": "#006847", "accent": "#8F8F8C"}},
    "MIN": {"full": "Minnesota Wild", "colors": {"bg": "#477124", "accent": "#792E4C"}},
    "MTL": {"full": "Montreal Canadiens", "colors": {"bg": "#AF1E2D", "accent": "#192168"}},
    "ANA": {"full": "Anaheim Ducks", "colors": {"bg": "#F47A38", "accent": "#B9975B"}},
    "PHI": {"full": "Philadelphia Flyers", "colors": {"bg": "#ED174C", "accent": "#000000"}},
    "UTA": {"full": "Utah Mammoth", "colors": {"bg": "#6CCEB2", "accent": "#192168"}},
    "EDM": {"full": "Edmonton Oilers", "colors": {"bg": "#FFB81C", "accent": "#041E42"}},
    "PIT": {"full": "Pittsburgh Penguins", "colors": {"bg": "#FCB514", "accent": "#000000"}},
    "BOS": {"full": "Boston Bruins", "colors": {"bg": "#000000", "accent": "#FFB81C"}},
    "LAK": {"full": "Los Angeles Kings", "colors": {"bg": "#111111", "accent": "#A2AAAD"}},
    "OTT": {"full": "Ottawa Senators", "colors": {"bg": "#C52032", "accent": "#000000"}},
}

EXPECTED_ABBRS = set(ABBR_INFO.keys())


def fetch_url(url, timeout=15):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [FAIL] {url}: {type(e).__name__}: {e}")
        return None


def parse_espn_futures(html):
    """Extract Stanley Cup futures odds from ESPN embedded JSON."""
    sc_marker = '"title":"Stanley Cup Winner"'
    sc_idx = html.find(sc_marker)
    if sc_idx < 0:
        return [], "No Stanley Cup section"

    # Find rows array after the marker ({"title":"...","rows":[...]})
    rows_idx = html.find('"rows"', sc_idx)
    if rows_idx < 0:
        return [], "No rows array"

    arr_start = html.find("[", rows_idx)
    if arr_start < 0:
        return [], "No array start"

    # Find matching ] by bracket counting
    depth = 0
    arr_end = arr_start
    for i in range(arr_start, min(arr_start + 50_000, len(html))):
        c = html[i]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                arr_end = i + 1
                break

    if depth != 0:
        return [], "Could not find array end"

    try:
        rows = json.loads(html[arr_start:arr_end])
    except json.JSONDecodeError as e:
        return [], f"JSON parse error: {e}"

    teams = []
    for row in rows:
        abbr = row.get("primaryText", "")
        odds_str = row.get("odds", "")
        full_name = row.get("primaryTextFull", "")
        if not abbr or not odds_str:
            continue

        info = ABBR_INFO.get(abbr, {})
        full_name = full_name or info.get("full", abbr)
        colors = info.get("colors", {"bg": "#000000", "accent": "#FFFFFF"})

        prob = calc_probability(odds_str)
        tier = assign_tier(prob)

        teams.append({
            "name": full_name,
            "abbr": abbr,
            "odds": odds_str,
            "prob": round(prob, 1),
            "tier": tier,
            "status": "Live odds",
            "_colors": colors,
        })

    teams.sort(key=lambda t: int(re.sub(r"[^\d-]", "", t["odds"])))
    return teams, None


def calc_probability(odds_str):
    try:
        val = int(re.sub(r"[^\d-]", "", odds_str))
        if val > 0:
            return 100 / (val + 100) * 100
        elif val < 0:
            return abs(val) / (abs(val) + 100) * 100
        return 50.0
    except (ValueError, TypeError):
        return 0.5


def assign_tier(prob):
    if prob >= 9:
        return "fav"
    if prob >= 3:
        return "con"
    return "horse"


def enhance_status(teams, espn_bracket_html):
    if not espn_bracket_html:
        return
    for t in teams:
        abbr = t.get("abbr")
        if abbr == "COL" and ("Avalanche wins series" in espn_bracket_html or "COL" in espn_bracket_html):
            t["status"] = "Adv - Swept Kings 4-0"
        elif abbr == "CAR" and ("Hurricanes wins series" in espn_bracket_html or "CAR wins series" in espn_bracket_html):
            t["status"] = "Adv - Swept Senators 4-0"


def download_logos(team_abbrs):
    os.makedirs(LOGOS_DIR, exist_ok=True)
    downloaded = 0
    for abbr in team_abbrs:
        path = os.path.join(LOGOS_DIR, f"{abbr}_light.svg")
        if os.path.exists(path):
            continue
        url = f"https://assets.nhle.com/logos/nhl/svg/{abbr}_light.svg"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                with open(path, "wb") as f:
                    f.write(resp.read())
                downloaded += 1
        except Exception:
            pass
    return downloaded


def load_cached_json():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_json(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    print("=" * 60)
    print("  STANLEY CUP ODDS UPDATER")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    sources_used = []
    teams = []

    # Step 1: ESPN Futures (PRIMARY - gives real JSON)
    print("\n[1/3] Fetching ESPN Futures for Stanley Cup odds...")
    espn_html = fetch_url("https://www.espn.com/nhl/futures")
    if espn_html:
        parsed_teams, err = parse_espn_futures(espn_html)
        if parsed_teams:
            teams = parsed_teams
            sources_used.append("espn")
            print(f"  [OK] Parsed {len(teams)} teams from ESPN Futures")
        else:
            print(f"  [FAIL] ESPN parsing: {err}")

    # Step 2: ESPN bracket for status info
    print("\n[2/3] Fetching ESPN playoff bracket for status...")
    bracket_html = fetch_url("https://www.espn.com/nhl/playoff-bracket")
    if bracket_html:
        sources_used.append("espn_bracket")
        enhance_status(teams, bracket_html)
        print("  [OK] Bracket fetched, status updated")
    else:
        print("  [FAIL] Bracket fetch failed")

    # Fallback: cached JSON
    if len(teams) < 10:
        print(f"\n[FALLBACK] Only {len(teams)} teams. Loading cache...")
        cached = load_cached_json()
        if cached and "teams" in cached:
            teams = cached["teams"]
            print(f"  [OK] Loaded {len(teams)} teams from cache")
            sources_used.append("cached")
        else:
            print("  [FAIL] No cache available")
            sys.exit(1)

    # Step 3: Logos
    team_abbrs = [t["abbr"] for t in teams]
    print(f"\n[3/3] Syncing logos...")
    new_logos = download_logos(team_abbrs)
    print(f"  [OK] {new_logos} new logos (cached: {len(team_abbrs) - new_logos})")

    # Build output
    team_colors = {}
    cleaned_teams = []
    for t in teams:
        abbr = t["abbr"]
        colors = t.pop("_colors", ABBR_INFO.get(abbr, {}).get("colors", {"bg": "#000", "accent": "#FFF"}))
        team_colors[abbr] = colors
        cleaned_teams.append(t)

    present_abbrs = set(t["abbr"] for t in cleaned_teams)
    eliminated = [
        ABBR_INFO[k]["full"]
        for k in sorted(EXPECTED_ABBRS - present_abbrs)
        if k in ABBR_INFO
    ]

    data = {
        "metadata": {
            "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sources": sources_used or ["cached"],
            "teamsRemaining": len(cleaned_teams),
            "eliminated": eliminated,
            "season": "2025-26",
        },
        "teamColors": team_colors,
        "teams": cleaned_teams,
    }

    save_json(data)
    print(f"\n[OK] Saved data/odds.json ({len(cleaned_teams)} teams)")
    print(f"[OK] Sources: {', '.join(sources_used)}")
    print(f"[OK] Updated: {data['metadata']['lastUpdated']}")
    print("=" * 60)
    sys.exit(0)


if __name__ == "__main__":
    main()
