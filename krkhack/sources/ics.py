"""Generic iCalendar subscription source (Meetup group feeds, Luma calendars, university calendars...).
ICS is the one format designed for machine consumption, so these feeds almost never break.
Config: feeds: [{name, url}]. Only events whose titles look hackathon-ish are kept downstream."""
from __future__ import annotations

import datetime as dt
import re
from zoneinfo import ZoneInfo

from ..model import Cand
from ..util import WAW, clean_text, http


def _unfold(text: str) -> list[str]:
    return re.sub(r"\r?\n[ \t]", "", text).splitlines()


def _unescape(v: str) -> str:
    return v.replace("\\n", " ").replace("\\N", " ").replace("\\,", ",").replace("\\;", ";").replace("\\\\", "\\")


def _dt(name_params: str, value: str):
    params = dict(p.split("=", 1) for p in name_params.split(";")[1:] if "=" in p)
    value = value.strip()
    if params.get("VALUE") == "DATE" or re.fullmatch(r"\d{8}", value):
        return dt.datetime.strptime(value[:8], "%Y%m%d").date()
    m = re.fullmatch(r"(\d{8}T\d{6})(Z?)", value)
    if not m:
        return None
    d = dt.datetime.strptime(m[1], "%Y%m%dT%H%M%S")
    if m[2]:
        return d.replace(tzinfo=dt.timezone.utc).astimezone(WAW)
    try:
        tz = ZoneInfo(params["TZID"]) if "TZID" in params else WAW
    except Exception:  # noqa: BLE001
        tz = WAW
    return d.replace(tzinfo=tz).astimezone(WAW)


def parse_ics(text: str, source: str) -> list[Cand]:
    out, cur = [], None
    for line in _unfold(text):
        if line == "BEGIN:VEVENT":
            cur = {}
        elif line == "END:VEVENT" and cur is not None:
            if cur.get("SUMMARY") and cur.get("DTSTART"):
                out.append(Cand(title=clean_text(_unescape(cur["SUMMARY"])), url=cur.get("URL") or "",
                                source=source, start=cur["DTSTART"], end=cur.get("DTEND"),
                                location=_unescape(cur.get("LOCATION", "")),
                                summary=clean_text(_unescape(cur.get("DESCRIPTION", "")), 300)))
            cur = None
        elif cur is not None and ":" in line:
            k, v = line.split(":", 1)
            base = k.split(";")[0].upper()
            if base in ("DTSTART", "DTEND"):
                cur[base] = _dt(k, v)
            elif base in ("SUMMARY", "URL", "LOCATION", "DESCRIPTION"):
                cur[base] = v
    return out


def fetch(cfg: dict, warn) -> list[Cand]:
    out = []
    for feed in cfg.get("feeds", []):
        try:
            cands = parse_ics(http(feed["url"]).text, f"ics:{feed['name']}")
            for c in cands:
                c.country = c.country or feed.get("country")
                c.location = c.location or feed.get("default_location", "")
            out += cands
        except Exception as ex:  # noqa: BLE001
            warn(f"{feed['name']}: {ex}")
    return out
