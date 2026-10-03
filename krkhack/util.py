"""HTTP + date helpers shared by all sources."""
from __future__ import annotations

import datetime as dt
import logging
import re
import time
from zoneinfo import ZoneInfo

import requests

log = logging.getLogger("krkhack")
WAW = ZoneInfo("Europe/Warsaw")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 krkhack-aggregator/1.0")

_session = requests.Session()
_session.headers.update({"User-Agent": UA, "Accept-Language": "en,pl;q=0.8"})


class FetchError(RuntimeError):
    pass


def http(url: str, *, method: str = "GET", params=None, json=None, headers=None,
         timeout: int = 30, retries: int = 2, impersonate: bool = False) -> requests.Response:
    """GET/POST with retries. If a plain request is blocked (403/429/503, typically
    Cloudflare TLS fingerprinting) we transparently retry with curl_cffi Chrome impersonation."""
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            if impersonate:
                r = _curl(url, method, params, json, headers, timeout)
            else:
                r = _session.request(method, url, params=params, json=json, headers=headers, timeout=timeout)
                if r.status_code in (403, 429, 503) and attempt == 0:
                    try:
                        r = _curl(url, method, params, json, headers, timeout)
                    except Exception as ex:  # curl_cffi missing/blocked: keep original response
                        log.debug("impersonation fallback failed for %s: %s", url, ex)
            if r.status_code >= 500 and attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            r.raise_for_status()
            # servers often omit the charset for text/* (requests then guesses Latin-1): force UTF-8
            if "charset" not in r.headers.get("content-type", "").lower():
                r.encoding = "utf-8"
            return r
        except Exception as ex:  # noqa: BLE001 - adapters want one uniform error
            last = ex
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise FetchError(f"{method} {url}: {last}")


def _curl(url, method, params, json, headers, timeout):
    from curl_cffi import requests as cr  # lazy: optional dependency
    return cr.request(method, url, params=params, json=json, headers=headers,
                      timeout=timeout, impersonate="chrome")


# ---------------------------------------------------------------- dates
def today() -> dt.date:
    return dt.datetime.now(WAW).date()


def parse_iso(s: str | None) -> dt.datetime | dt.date | None:
    """ISO string -> Warsaw-local aware datetime (if time present) or date."""
    if not s:
        return None
    s = s.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        return dt.date.fromisoformat(s)
    try:
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        return d.replace(tzinfo=WAW)
    return d.astimezone(WAW)


def iso(d: dt.datetime | dt.date | None) -> str | None:
    if d is None:
        return None
    if isinstance(d, dt.datetime):
        return d.astimezone(WAW).strftime("%Y-%m-%dT%H:%M")
    return d.isoformat()


def as_date(d: dt.datetime | dt.date) -> dt.date:
    return d.astimezone(WAW).date() if isinstance(d, dt.datetime) else d


_MONTHS_EN = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
_MONTHS_PL = {"stycze": 1, "luty": 2, "lutego": 2, "marz": 3, "kwie": 4, "maj": 5, "czerw": 6,
              "lipi": 7, "sierp": 8, "wrze": 9, "pa\u017adz": 10, "listop": 11, "grud": 12}


def month_pl(name: str) -> int | None:
    n = name.strip().lower()
    for k, v in _MONTHS_PL.items():
        if n.startswith(k):
            return v
    return None


def parse_devpost_range(s: str) -> tuple[dt.date, dt.date] | None:
    """'Mar 28 - 29, 2026' | 'Oct 06, 2026 - Jan 12, 2027' | 'Dec 28 - Jan 04, 2027'."""
    m = re.match(r"\s*([A-Za-z]{3})[a-z]*\s+(\d{1,2})(?:,\s*(\d{4}))?\s*-\s*(?:([A-Za-z]{3})[a-z]*\s+)?(\d{1,2}),\s*(\d{4})", s or "")
    if not m:
        m1 = re.match(r"\s*([A-Za-z]{3})[a-z]*\s+(\d{1,2}),\s*(\d{4})\s*$", s or "")
        if m1:
            d = dt.date(int(m1[3]), _MONTHS_EN[m1[1].lower()], int(m1[2]))
            return d, d
        return None
    mo1, d1, y1, mo2, d2, y2 = m.groups()
    mo1n = _MONTHS_EN.get(mo1.lower())
    mo2n = _MONTHS_EN.get((mo2 or mo1).lower())
    if not mo1n or not mo2n:
        return None
    y2 = int(y2)
    y1 = int(y1) if y1 else (y2 - 1 if mo1n > mo2n else y2)
    try:
        return dt.date(y1, mo1n, int(d1)), dt.date(y2, mo2n, int(d2))
    except ValueError:
        return None


def clean_text(s: str | None, limit: int = 0) -> str:
    import html as _html
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = _html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:limit].rstrip() + ("\u2026" if limit and len(s) > limit else "") if limit else s
