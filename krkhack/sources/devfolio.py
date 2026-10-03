"""Devfolio public search API; only Poland-based events (their online hackathons skew India-only)."""
from __future__ import annotations

from ..model import Cand
from ..util import clean_text, http, parse_iso, seen


def fetch(cfg: dict, warn) -> list[Cand]:
    out = []
    off = 0
    while off < 400:
        d = http("https://api.devfolio.co/api/search/hackathons", method="POST",
                 json={"type": "application_open", "from": off, "size": 100}).json()
        hits = [h["_source"] for h in d.get("hits", {}).get("hits", [])]
        if not hits:
            break
        seen(warn, len(hits))
        for h in hits:
            if h.get("country") != "Poland":
                continue
            out.append(Cand(
                title=h["name"], url=f"https://{h['slug']}.devfolio.co", source="devfolio",
                start=parse_iso(h.get("starts_at")), end=parse_iso(h.get("ends_at")),
                location=h.get("location") or h.get("city") or "", country="PL", online=bool(h.get("is_online")),
                kind_hint="hackathon", summary=clean_text(h.get("tagline"), 200)))
        off += 100
    return [c for c in out if c.start]
