"""CTFtime public API: on-site CTFs located in Poland (online CTFs run weekly worldwide - too noisy)."""
from __future__ import annotations

import datetime as dt

from ..model import Cand
from ..util import clean_text, http, parse_iso, today


def fetch(cfg: dict, warn) -> list[Cand]:
    start = dt.datetime.combine(today(), dt.time.min)
    finish = start + dt.timedelta(days=400)
    rows = http("https://ctftime.org/api/v1/events/",
                params={"limit": 200, "start": int(start.timestamp()), "finish": int(finish.timestamp())}).json()
    out = []
    for r in rows:
        loc = r.get("location") or ""
        if not (r.get("onsite") and ("poland" in loc.lower() or "krak" in loc.lower() or "polska" in loc.lower())):
            continue
        out.append(Cand(title=clean_text(r["title"]), url=r.get("url") or r["ctftime_url"], source="ctftime",
                        start=parse_iso(r["start"]), end=parse_iso(r["finish"]), location=loc, country="PL",
                        online=False, kind_hint="ctf", summary=clean_text(r.get("description"), 250)))
    return out
