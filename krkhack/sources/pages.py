"""Schema.org JSON-LD scraper for a configurable list of pages (dev.events, GDG chapter pages,
Meetup group pages, organizer sites...). Config: pages: [{name, url}]"""
from __future__ import annotations

from ..jsonld import events_from_html
from ..model import Cand
from ..util import http


def fetch(cfg: dict, warn) -> list[Cand]:
    out = []
    for p in cfg.get("pages", []):
        try:
            cands = events_from_html(http(p["url"]).text, p["url"], f"page:{p['name']}")
            for c in cands:
                c.country = c.country or p.get("country")
            out += cands
        except Exception as ex:  # noqa: BLE001
            warn(f"{p['name']}: {ex}")
    return out
