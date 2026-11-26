#!/usr/bin/env python3
"""Pull public Sleeper data and write js/data-league.js in the original L shape.

Does not overwrite story text, art, or the 2025 trophy record
(data/seasons-2025.json). Re-run after scores finalize, typically Tuesday.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAGUE_ID = "1312073772823490560"
API = "https://api.sleeper.app/v1"

# Official names, handles and abbreviations, keyed by Sleeper user_id.
TEAMS = {
    "463339730302398464": {"id": 1, "name": "The Eternal Legion", "handle": "williampmcneil", "commish": True, "abbr": "LEG"},
    "458462348034699264": {"id": 2, "name": "Go Go Bower Rangers!", "handle": "MegaMann87", "commish": False, "abbr": "BOW"},
    "462772233568251904": {"id": 3, "name": "Sunday Executioners", "handle": "chaddferro", "commish": False, "abbr": "EXE"},
    "470032147768406016": {"id": 4, "name": "Sunday Scaries", "handle": "JFalco11", "commish": False, "abbr": "SCA"},
    "470427757860352000": {"id": 5, "name": "Team Casello", "handle": "Casello", "commish": False, "abbr": "CAS"},
    "992182267713830912": {"id": 6, "name": "Team PhilDaThrill420", "handle": "PhilDaThrill420", "commish": False, "abbr": "PHI"},
    "655478222066102272": {"id": 7, "name": "The Picklers", "handle": "Mattsgirlakabilly", "commish": False, "abbr": "PIC"},
    "721547129281150976": {"id": 8, "name": "Laggys Mean Machine", "handle": "laggy96", "commish": False, "abbr": "LAG"},
    "1264057516417884160": {"id": 9, "name": "ChatGPG", "handle": "gguerin8", "commish": False, "abbr": "GPG"},
    "470393855800242176": {"id": 10, "name": "Rest & Rebuild", "handle": "jvarsam", "commish": False, "abbr": "R&R"},
}


def get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "GDE-newsletter/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fmt_pts(n) -> float:
    return round(float(n or 0), 2)


def pulled_label() -> str:
    # e.g. "Nov 22, 2026" — same shape as the original page
    d = date.today()
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def games_for_week(raw):
    """Return [[id, pts, id, pts], ...] in Sleeper matchup_id order.

    Team order inside a pair follows the API response, so rematch weeks
    keep the same slot numbers as earlier meetings (w10/m1 lines up with w1/m1).
    """
    by_id = defaultdict(list)
    for row in raw:
        mid = row.get("matchup_id")
        if mid is None:
            continue
        by_id[mid].append((row.get("roster_id"), fmt_pts(row.get("points") or 0)))
    games = []
    for mid in sorted(by_id):
        teams = by_id[mid]
        if len(teams) != 2:
            continue
        (a, pa), (b, pb) = teams
        games.append([a, pa, b, pb])
    return games


def main() -> int:
    print("Pulling Sleeper public API…")
    league = get(f"{API}/league/{LEAGUE_ID}")
    users = get(f"{API}/league/{LEAGUE_ID}/users")
    rosters = get(f"{API}/league/{LEAGUE_ID}/rosters")
    state = get(f"{API}/state/nfl")

    settings = league.get("settings") or {}
    last_scored = int(settings.get("last_scored_leg") or 0)
    current_week = int(state.get("week") or settings.get("leg") or last_scored)

    # roster_id is stable and matches the official id in TEAMS
    teams = []
    owner_of = {r["roster_id"]: str(r.get("owner_id")) for r in rosters}
    for rid in range(1, 11):
        official = TEAMS.get(owner_of.get(rid), {})
        if not official:
            # Fallback: keep the roster id and whatever Sleeper has
            user = next((u for u in users if str(u.get("user_id")) == owner_of.get(rid)), {})
            official = {
                "id": rid,
                "name": ((user.get("metadata") or {}).get("team_name") or user.get("display_name") or f"Roster {rid}").strip(),
                "handle": user.get("display_name") or "",
                "commish": bool(user.get("is_owner")),
                "abbr": (user.get("display_name") or "TM")[:3].upper(),
            }
        else:
            official = dict(official)
            official["id"] = rid
        teams.append(official)

    weeks = {}
    for w in range(1, last_scored + 1):
        raw = get(f"{API}/league/{LEAGUE_ID}/matchups/{w}")
        weeks[str(w)] = games_for_week(raw)

    slate = None
    if current_week > last_scored:
        raw = get(f"{API}/league/{LEAGUE_ID}/matchups/{current_week}")
        pairs = [[g[0], g[2]] for g in games_for_week(raw)]
        if pairs:
            slate = {"week": current_week, "games": pairs}

    seasons_path = ROOT / "data" / "seasons-2025.json"
    seasons = json.loads(seasons_path.read_text()) if seasons_path.exists() else []

    champ = None
    if seasons:
        champ = seasons[-1].get("champ")

    L = {
        "id": str(league.get("league_id") or LEAGUE_ID),
        "name": league.get("name") or "The Greatest Dynasty Ever",
        "season": int(league.get("season") or 2026),
        "currentWeek": current_week,
        "lastScoredWeek": last_scored,
        "playoffWeekStart": int(settings.get("playoff_week_start") or 15),
        "playoffTeams": int(settings.get("playoff_teams") or 6),
        "champRosterId": champ,
        "pulled": pulled_label(),
        "teams": teams,
        "weeks": weeks,
        "slate": slate,
        "seasons": seasons,
    }

    dest = ROOT / "js" / "data-league.js"
    dest.write_text(
        "/* ===== League data, pulled from Sleeper. Replaced on each weekly publish. ===== */\n"
        "const L = "
        + json.dumps(L, ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    print(
        f"  wrote {dest.relative_to(ROOT)}  season={L['season']} "
        f"current={current_week} last_scored={last_scored} weeks={len(weeks)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
