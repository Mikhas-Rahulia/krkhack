"""Luma discover API. Krakow isn't a launched 'place', so: (a) lat/lon feed around Krakow, plus
(b) global text queries filtered client-side to Poland/online. Everything is client-side filtered."""
from __future__ import annotations

from ..classify import kind_of
from ..model import Cand
from ..util import clean_text, http, parse_iso

API = "https://api.lu.ma/discover/get-paginated-events"
KRK = (50.0647, 19.945)
QUERIES = ["hackathon", "hackathon poland", "hackathon krakow", "game jam", "buildathon", "ctf"]


def _entries(params: dict, pages: int = 3):
    cursor = None
    for _ in range(pages):
        p = {**params, "pagination_limit": 50}
        if cursor:
            p["pagination_cursor"] = cursor
        d = http(API, params=p).json()
        yield from d.get("entries", [])
        if not d.get("has_more"):
            break
        cursor = d.get("next_cursor")


def fetch(cfg: dict, warn) -> list[Cand]:
    seen: dict[str, Cand] = {}
    streams = [{"latitude": KRK[0], "longitude": KRK[1]}] + [{"query": q} for q in cfg.get("queries", QUERIES)]
    for params in streams:
        try:
            for e in _entries(params, pages=3 if "latitude" in params else 2):
                ev = e["event"]
                geo = ev.get("geo_address_info") or {}
                cc = geo.get("country_code")
                online = ev.get("location_type") == "online"
                near_stream = "latitude" in params
                if not (near_stream or cc == "PL" or online):
                    continue
                if not near_stream and not kind_of(ev["name"]):
                    continue
                start = parse_iso(ev.get("start_at"))
                if not start:
                    continue
                seen.setdefault(ev["api_id"], Cand(
                    title=clean_text(ev["name"]), url=f"https://lu.ma/{ev['url']}", source="luma",
                    start=start, end=parse_iso(ev.get("end_at")),
                    location=geo.get("full_address") or geo.get("city_state") or "", country=cc, online=online,
                    summary=clean_text(geo.get("description"), 200)))
        except Exception as ex:  # noqa: BLE001
            warn(f"{params}: {ex}")
    return list(seen.values())
