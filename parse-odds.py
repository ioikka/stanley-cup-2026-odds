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

# ── All known NHL playoff teams (complete list for fallback) ──
ALL_NHL_TEAMS = {
    "Avalanche":      {"abbr": "COL", "colors": {"bg": "#6F263D", "accent": "#236192"}},
    "Hurricanes":     {"abbr": "CAR", "colors": {"bg": "#CC0000", "accent": "#000000"}},
    "Lightning":      {"abbr": "TBL", "colors": {"bg": "#002868", "accent": "#005A90"}},
    "Golden Knights": {"abbr": "VGK", "colors": {"bg": "#B4975A", "accent": "#333F4C"}},
    "Sabres":         {"abbr": "BUF", "colors": {"bg": "#274488", "accent": "#FFB81C"}},
    "Stars":          {"abbr": "DAL", "colors": {"bg": "#006847", "accent": "#8F8F8C"}},
    "Wild":           {"abbr": "MIN", "colors": {"bg": "#477124", "accent": "#792E4C"}},
    "Canadiens":      {"abbr": "MTL", "colors": {"bg": "#AF1E2D", "accent": "#192168"}},
    "Ducks":          {"abbr": "ANA", "colors": {"bg": "#F47A38", "accent": "#B9975B"}},
    "Flyers":         {"abbr": "PHI", "colors": {"bg": "#ED174C", "accent": "#000000"}},
    "Mammoth":        {"abbr": "UTA", "colors": {"bg": "#6CCEB2", "accent": "#192168"}},
    "Oilers":         {"abbr": "EDM", "colors": {"bg": "#FFB81C", "accent": "#041E42"}},
    "Penguins":       {"abbr": "PIT", "colors": {"bg": "#FCB514", "accent": "#000000"}},
    "Bruins":         {"abbr": "BOS", "colors": {"bg": "#FFB81C", "accent": "#C8102E"}},
    "Kings":          {"abbr": "LAK", "colors": {"bg": "#111111", "accent": "#A2AAAD"}},
    "Senators":       {"abbr": "OTT", "colors": {"bg": "#C52032", "accent": "#000000"}}
}

def fetch_url(url, timeout=15):
    """Fetch URL content with error handling."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/json,text/plain,*/*",
            "Accept-Language": "en-US,en;q=0.9"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [!] Fetch failed ({url}): {type(e).__name__}: {e}")
        return None

def parse_action_network(html):
    """Parse Stanley Cup odds from The Action Network futures page."""
    if html is None:
        return None, {}

    teams = []
    team_odds = {}
    simplified_pattern = re.compile(
        r'(Avalanche|Hurricanes|Lightning|Golden\s*Knights|Sabres|Stars|Wild|Canadiens'
        r'|Ducks|Flyers|Mammoth|Mammoths|Oilers|Penguins|Bruins)'
        r'([^<]*?)\+(-?\d+)'
    )

    for match in simplified_pattern.finditer(html):
        team_name = match.group(1).strip().replace("\xa0", " ")
        odds_raw = match.group(3).strip()
        odds_str = f"+{odds_raw}" if odds_raw.lstrip("-").lstrip("+").isdigit() else odds_raw

        if team_name in ALL_NHL_TEAMS:
            team_odds[team_name] = odds_str

    # Build team list from matched odds
    name_to_key = {
        "Avalanche": "Avalanche", "Hurricanes": "Hurricanes", "Lightning": "Lightning",
        "Golden Knights": "Golden Knights", "Golden Knighth": "Golden Knights",
        "Sabres": "Sabres", "Stars": "Stars", "Wild": "Wild", "Canadiens": "Canadiens",
        "Ducks": "Ducks", "Flyers": "Flyers", "Mammoth": "Mammoth", "Mammoths": "Mammoth",
        "Oilers": "Oilers", "Penguins": "Penguins", "Bruins": "Bruins"
    }

    for name, odds_str in sorted(team_odds.items(), key=lambda x: parse_odds_number(x[1])):
        key = name_to_key.get(name)
        if key and key in ALL_NHL_TEAMS:
            info = ALL_NHL_TEAMS[key]
            prob = calc_implied_probability(odds_str)
            tier = assign_tier(prob)
            teams.append({
                "name": f"{key.split()[0]} {key.split(' ')[1] if len(key.split(' ')) > 1 else ''}".strip(),
                "full_name": f"{key} " if " " in key else f"{key} ",
                "abbr": info["abbr"],
                "odds": odds_str,
                "prob": round(prob, 1),
                "tier": tier,
                "status": "Live odds"
            })

    if teams:
        fixed = []
        for t in teams:
            abbr = t["abbr"]
            for k, v in ALL_NHL_TEAMS.items():
                if v["abbr"] == abbr:
                    t["full_name"], t["name"] = full_team_name(k), k
                    break
            fixed.append(t)
        return True, fixed
    return False, {}

def parse_odds_number(odds_str):
    """Convert odds string to comparable number."""
    try:
        return int(re.sub(r"[^-\d]", "", odds_str))
    except:
        return 0

def calc_implied_probability(odds_str):
    """Convert American odds to implied probability."""
    try:
        val = int(re.sub(r"[^-\d]", "", odds_str))
        if val > 0:
            return 100 / (val + 100) * 100
        elif val < 0:
            return abs(val) / (abs(val) + 100) * 100
        return 50.0
    except:
        return 0.5

def assign_tier(prob):
    """Assign tier based on probability."""
    if prob >= 9:
        return "fav"
    elif prob >= 3:
        return "con"
    return "horse"

def full_team_name(key):
    """Get full team name from short name."""
    mapping = {
        "Avalanche": "Colorado Avalanche", "Hurricanes": "Carolina Hurricanes",
        "Lightning": "Tampa Bay Lightning", "Golden Knights": "Vegas Golden Knights",
        "Sabres": "Buffalo Sabres", "Stars": "Dallas Stars", "Wild": "Minnesota Wild",
        "Canadiens": "Montreal Canadiens", "Ducks": "Anaheim Ducks", "Flyers": "Philadelphia Flyers",
        "Mammoth": "Utah Mammoth", "Oilers": "Edmonton Oilers", "Penguins": "Pittsburgh Penguins",
        "Bruins": "Boston Bruins", "Kings": "Los Angeles Kings", "Senators": "Ottawa Senators"
    }
    return mapping.get(key, key)

def parse_espn_bracket(html):
    """Parse ESPN playoff bracket for team status."""
    if html is None:
        return {}
    status = {}
    series_patterns = [
        (r"(\w+(?:\s+\w+)?)\s+vs\s+(\w+(?:\s+\w+)?)", {"match": True}),
    ]
    return status

def parse_espn_odds(html):
    """Parse team statuses from ESPN odds page."""
    if html is None:
        return {}
    statuses = {}
    series_matches = re.findall(
        r'(\w+)\s+[\d+-]+\s+(\w+)',
        html, re.DOTALL
    )
    return statuses

def download_logos(team_abbrs):
    """Download NHL team logos to local logos/ directory."""
    os.makedirs(LOGOS_DIR, exist_ok=True)
    downloaded = 0
    for abbr in team_abbrs:
        logo_path = os.path.join(LOGOS_DIR, f"{abbr}_light.svg")
        if os.path.exists(logo_path):
            continue
        url = f"https://assets.nhle.com/logos/nhl/svg/{abbr}_light.svg"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                with open(logo_path, "wb") as f:
                    f.write(resp.read())
                downloaded += 1
        except:
            pass
    return downloaded

def load_cached_json():
    """Load existing cached odds.json as fallback."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return None

def save_json(data):
    """Save data to odds.json."""
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
    eliminated = []

    # ── SOURCE 1: Action Network ──
    print("\n[1/3] Fetching Action Network Stanley Cup odds...")
    action_html = fetch_url("https://www.actionnetwork.com/nhl/futures")
    parsed, teams = parse_action_network(action_html)
    if parsed and teams:
        print(f"  [OK] Parsed {len(teams)} teams from Action Network")
        sources_used.append("action_network")
    else:
        print("  [FAIL] Action Network parsing failed")

    # ── SOURCE 2: ESPN ──
    print("\n[2/3] Fetching ESPN playoff bracket for status...")
    espn_html = fetch_url("https://www.espn.com/nhl/playoff-bracket")
    if espn_html:
        print("  [OK] ESPN bracket fetched (status parsing pending)")
        sources_used.append("espn")
        # Status enhancement from ESPN bracket
        if "Avalanche wins series" in espn_html:
            for t in teams:
                if t.get("abbr") == "COL":
                    t["status"] = "Adv · Swept Kings 4-0"
        if "Hurricanes wins series" in espn_html or "CAR wins series" in espn_html:
            for t in teams:
                if t.get("abbr") == "CAR":
                    t["status"] = "Adv · Swept Senators 4-0"
    else:
        print("  [FAIL] ESPN bracket fetch failed")

    # ── FALLBACK to cached JSON ──
    if not teams or len(teams) < 10:
        print(f"\n[FALLBACK] Only got {len(teams)} teams from online sources. Loading cached data...")
        cached = load_cached_json()
        if cached and "teams" in cached:
            teams = cached["teams"]
            eliminated = cached.get("metadata", {}).get("eliminated", [])
            print(f"  [OK] Loaded {len(teams)} teams from cache")
        else:
            print("  [FAIL] No cached data found. Cannot update.")
            return {"status": "error", "message": "All sources and cache failed"}

    # ── Download logos ──
    team_abbrs = [t["abbr"] for t in teams]
    print(f"\n[3/3] Syncing team logos...")
    new_logos = download_logos(team_abbrs)
    print(f"  [OK] Downloaded {new_logos} new logos (cached: {len(team_abbrs) - new_logos})")

    # ── Build and save JSON ──
    team_colors = {}
    for t in teams:
        abbr = t.get("abbr", "")
        if abbr in ALL_NHL_TEAMS:
            team_colors[abbr] = ALL_NHL_TEAMS[abbr]["colors"]
        else:
            for k, v in ALL_NHL_TEAMS.items():
                if v["abbr"] == abbr or k in t.get("name", "") or k in t.get("full_name", ""):
                    team_colors[abbr] = v["colors"]
                    break

    # Detect eliminated teams
    all_expected = set(ALL_NHL_TEAMS.keys())
    team_names = set(t.get("name", "") for t in teams)
    team_abbrs = set(t.get("abbr", "") for t in teams)
    eliminated = [
        full_team_name(k) for k in all_expected 
        if full_team_name(k) not in team_names and ALL_NHL_TEAMS[k]["abbr"] not in team_abbrs
    ]

    data = {
        "metadata": {
            "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sources": sources_used if sources_used else ["cached"],
            "teamsRemaining": len(teams),
            "eliminated": eliminated,
            "season": "2025-26"
        },
        "teamColors": team_colors,
        "teams": teams
    }

    save_json(data)
    print(f"\n[OK] Saved data/odds.json ({len(teams)} teams)")
    print(f"[OK] Sources: {', '.join(sources_used) if sources_used else 'cached'}")
    print(f"[OK] Updated: {data['metadata']['lastUpdated']}")
    print("=" * 60)

    return data

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result and result.get("status", True) != "error" else 1)
