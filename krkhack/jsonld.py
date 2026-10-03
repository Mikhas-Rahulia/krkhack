"""Extract schema.org Event objects from any HTML page. Works on Meetup, GDG, dev.events,
many organizer sites; the cheapest, most maintenance-free structured extraction there is."""
from __future__ import annotations

import json
import re

from .model import Cand
from .util import clean_text, parse_iso

_LD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)


def _walk(o):
    if isinstance(o, list):
        for x in o:
            yield from _walk(x)
    elif isinstance(o, dict):
        t = o.get("@type")
        ts = t if isinstance(t, list) else [t]
        if any(isinstance(x, str) and x.endswith("Event") for x in ts):
            yield o
        for k in ("@graph", "itemListElement", "item", "event", "subEvent", "mainEntity"):
            if k in o:
                yield from _walk(o[k])


def _loc(o: dict) -> tuple[str, str | None, bool | None]:
    loc = o.get("location")
    locs = loc if isinstance(loc, list) else [loc]
    parts, country, online = [], None, None
    for l in locs:
        if isinstance(l, str):
            parts.append(l)
        elif isinstance(l, dict):
            if "VirtualLocation" in str(l.get("@type")):
                online = True
                continue
            parts.append(str(l.get("name") or ""))
            a = l.get("address")
            if isinstance(a, dict):
                parts += [str(a.get(k) or "") for k in ("streetAddress", "addressLocality", "addressRegion")]
                c = a.get("addressCountry")
                country = (c.get("name") if isinstance(c, dict) else c) or country
            elif isinstance(a, str):
                parts.append(a)
    mode = str(o.get("eventAttendanceMode") or "")
    if "Online" in mode and "Mixed" not in mode:
        online = True
    if isinstance(country, str) and len(country) > 2:
        country = {"poland": "PL", "polska": "PL"}.get(country.lower(), country)
    uniq: list[str] = []
    for p in (x.strip() for x in parts):
        if p and not any(p.lower() in u.lower() for u in uniq):
            uniq.append(p)
    return ", ".join(uniq), country, online


def events_from_html(html: str, base_url: str, source: str) -> list[Cand]:
    out: list[Cand] = []
    for m in _LD.finditer(html or ""):
        try:
            data = json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            continue
        for o in _walk(data):
            name = clean_text(str(o.get("name") or ""))
            start = parse_iso(o.get("startDate"))
            if not name or not start:
                continue
            location, country, online = _loc(o)
            url = o.get("url") or base_url
            if isinstance(url, str) and url.startswith("/"):
                from urllib.parse import urljoin
                url = urljoin(base_url, url)
            out.append(Cand(title=name, url=str(url), source=source, start=start,
                            end=parse_iso(o.get("endDate")), location=location, country=country,
                            online=online, summary=clean_text(str(o.get("description") or ""), 400)))
    return out
