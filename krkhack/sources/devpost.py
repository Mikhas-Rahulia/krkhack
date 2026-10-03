"""Devpost unofficial JSON API. `search` matches title+venue only (location filter is ignored),
so we run several Krakow-flavoured terms plus an 'online & open to public' sweep."""
from __future__ import annotations

from ..model import Cand
from ..util import clean_text, http, parse_devpost_range

API = "https://devpost.com/api/hackathons"
TERMS = ["krakow", "krak\u00f3w", "cracow", "Poland", "Polska", "Hacknarok", "AGH", "Zab\u0142ocie"]


def _pages(params: dict, max_pages: int = 4):
    for page in range(1, max_pages + 1):
        d = http(API, params={**params, "per_page": 50, "page": page}).json()
        yield from d.get("hackathons", [])
        meta = d.get("meta", {})
        if page * meta.get("per_page", 50) >= meta.get("total_count", 0) or not d.get("hackathons"):
            break


def _cand(h: dict, online: bool | None) -> Cand | None:
    rng = parse_devpost_range(h.get("submission_period_dates", ""))
    if not rng or h.get("open_state") == "ended":
        return None
    loc = (h.get("displayed_location") or {}).get("location", "").strip()
    themes = ", ".join(t["name"] for t in h.get("themes", []))
    prize = clean_text(h.get("prize_amount"))
    return Cand(title=h["title"].strip(), url=h["url"].split("?")[0], source="devpost", start=rng[0], end=rng[1],
                location=loc, online=online if online is not None else (loc.lower() == "online"),
                kind_hint="hackathon",
                summary=" \u00b7 ".join(x for x in (themes, prize and f"Prize: {prize}") if x),
                extra={"devpost_id": h["id"], "invite_only": h.get("invite_only")})


def fetch(cfg: dict, warn) -> list[Cand]:
    found: dict[int, Cand] = {}
    for term in cfg.get("terms", TERMS):
        for h in _pages({"search": term, "status[]": ["upcoming", "open"]}):
            c = _cand(h, None)
            if c:
                found[h["id"]] = c
    if cfg.get("online", True):
        for h in _pages({"status[]": ["upcoming", "open"], "challenge_type[]": "online", "open_to[]": "public"}, 3):
            c = _cand(h, True)
            if c and h["id"] not in found:
                found[h["id"]] = c
    return list(found.values())
