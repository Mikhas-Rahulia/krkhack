"""MLH season pages embed Inertia JSON. We keep digital events and anything physically in Poland."""
from __future__ import annotations

import json
import re

from ..model import Cand
from ..util import http, parse_iso, seen, today

_DATA = re.compile(r'<script data-page="app" type="application/json">(.*?)</script>', re.S)


def fetch(cfg: dict, warn) -> list[Cand]:
    out = []
    for year in (today().year, today().year + 1):
        try:
            html = http(f"https://www.mlh.com/seasons/{year}/events").text
        except Exception as ex:  # noqa: BLE001 - next season page may not exist yet
            warn(f"season {year}: {ex}")
            continue
        m = _DATA.search(html)
        if not m:
            warn(f"season {year}: embedded JSON not found (markup changed?)")
            continue
        props = json.loads(m.group(1)).get("props", {})
        seen(warn, len(props.get("upcomingEvents", [])) + len(props.get("pastEvents", [])))
        for e in props.get("upcomingEvents", []):
            va = e.get("venueAddress") or {}
            digital = e.get("formatType") == "digital"
            if not (digital or va.get("country") == "PL"):
                continue
            out.append(Cand(
                title=e["name"], url=e.get("websiteUrl") or "https://www.mlh.com" + e["url"], source="mlh",
                start=parse_iso(e.get("startsAt")), end=parse_iso(e.get("endsAt")),
                location="Online" if digital else (e.get("location") or ""), country=va.get("country"),
                online=digital, kind_hint="hackathon", summary="Student hackathon (MLH)"))
    return [c for c in out if c.start]
