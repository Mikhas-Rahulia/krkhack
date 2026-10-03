"""GDG chapters (Bevy platform) - clean JSON API. DevFest-style events sometimes include hackathons."""
from __future__ import annotations

from ..model import Cand
from ..util import clean_text, http, parse_iso, seen


def fetch(cfg: dict, warn) -> list[Cand]:
    out = []
    for ch in cfg.get("chapters", [{"id": 578, "name": "GDG Krak\u00f3w", "city": "Krak\u00f3w"}]):
        try:
            # (the API 400s on unknown query params; the bare endpoint returns the chapter's events)
            d = http(f"https://gdg.community.dev/api/event_slim/for_chapter/{ch['id']}/").json()
            seen(warn, len(d.get("results", [])))
            for e in d.get("results", []):
                start = parse_iso(e.get("start_date"))
                if not start:
                    continue
                url = e.get("static_url") or e.get("url") or f"https://gdg.community.dev/gdg-{ch['name'].split()[-1].lower()}/"
                out.append(Cand(title=clean_text(e["title"]), url=url, source=f"gdg:{ch['name']}", start=start,
                                end=parse_iso(e.get("end_date")), country="PL",
                                online=bool(e.get("is_virtual_event")), location=ch.get("city", ""),
                                summary=clean_text(e.get("description_short"), 300)))
        except Exception as ex:  # noqa: BLE001
            warn(f"{ch['name']}: {ex}")
    return out
