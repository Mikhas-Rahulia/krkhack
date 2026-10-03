"""Recurring-series watchlist. This is what keeps the feed 'full' in a city with only ~25 public
hackathons a year: annual events are listed as EXPECTED (with a month window and a link) until the
real dates are announced, at which point a confirmed event from any source replaces the placeholder."""
from __future__ import annotations

import calendar
import datetime as dt
import re
from pathlib import Path

import yaml

from .classify import audience_of
from .jsonld import events_from_html
from .model import Cand
from .util import as_date, http, today

FILE = Path(__file__).resolve().parents[1] / "data" / "series.yml"


def load() -> list[dict]:
    data = yaml.safe_load(FILE.read_text(encoding="utf-8")) or []
    for s in data:
        s["_re"] = re.compile(s["match"], re.I)
    return data


def patterns(series: list[dict]) -> list[re.Pattern]:
    return [s["_re"] for s in series]


def match(series: list[dict], title: str) -> dict | None:
    for s in series:
        if s["_re"].search(title):
            return s
    return None


def next_window(months: list[int], after_end: dt.date | None, ref: dt.date) -> tuple[dt.date, dt.date] | None:
    """Earliest typical-month window that is not over yet and doesn't immediately follow the last edition."""
    for yr in (ref.year, ref.year + 1, ref.year + 2):
        for m in sorted(months):
            start = dt.date(yr, m, 1)
            end = dt.date(yr, m, calendar.monthrange(yr, m)[1])
            if end < ref:
                continue
            if after_end and start < after_end + dt.timedelta(days=150):
                continue
            return start, end
    return None


def expected_events(series: list[dict], confirmed: list[dict], last_seen: dict[str, str], ref: dt.date) -> list[dict]:
    """Placeholder entries for series with no confirmed upcoming edition."""
    out = []
    for s in series:
        if s.get("tier") == "skip" or not s.get("months"):
            continue
        has_future = any(s["_re"].search(e["title"]) for e in confirmed)
        if has_future:
            continue
        la = dt.date.fromisoformat(last_seen[s["id"]]) if s["id"] in last_seen else None
        w = next_window(s["months"], la, ref)
        if not w:
            continue
        # only show placeholders within the horizon so the page stays relevant
        if (w[0] - ref).days > int(s.get("horizon_days", 200)):
            continue
        out.append({
            "title": s["name"], "url": s["url"], "start": w[0].isoformat(), "end": w[1].isoformat(),
            "precision": "month", "location": s.get("location", "Krak\u00f3w"), "tier": s.get("tier", "krakow"),
            "kind": s.get("kind", "hackathon"), "status": "expected", "online": bool(s.get("online", False)),
            "summary": s.get("note", ""), "audience": s.get("audience") or audience_of(s["name"]),
            "sources": ["series"], "links": [{"source": "series", "url": s["url"]}], "series": s["id"],
        })
    return out


def check_pages(series: list[dict], warn) -> list[Cand]:
    """Cheap self-healing: look for schema.org Events on each series' own site(s)."""
    out = []
    for s in series:
        for u in ([s["url"]] if s.get("url") else []) + list(s.get("check", [])):
            if "linkedin.com" in u or "facebook.com" in u:
                continue
            try:
                for c in events_from_html(http(u, timeout=20, retries=1).text, u, f"series:{s['id']}"):
                    if s["_re"].search(c.title) and as_date(c.start) >= today():
                        c.kind_hint = c.kind_hint or "hackathon"
                        out.append(c)
            except Exception as ex:  # noqa: BLE001 - sites come and go; never fatal
                warn(f"{s['id']} {u}: {str(ex)[:120]}")
    return out
