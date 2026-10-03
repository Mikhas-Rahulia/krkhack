"""Crossweb.pl - the largest Polish IT-event database. Cloudflare-protected: util.http falls back
to curl_cffi Chrome impersonation automatically. Two independent paths so one breaking is not fatal:
  1) HTML search/list pages (rich: all cities, type column)
  2) RSS for the Krakow list (simple, stable)"""
from __future__ import annotations

import datetime as dt
import re
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup
from lxml import etree as ET

from ..model import Cand
from ..util import WAW, clean_text, http, month_pl

BASE = "https://crossweb.pl"
PAGES = [
    "/wyszukiwarka/?fraza=hackathon",
    "/wyszukiwarka/?fraza=hakaton",
    "/wyszukiwarka/?fraza=game+jam",
    "/wyszukiwarka/?fraza=CTF",
    "/wydarzenia/krakow/",
    "/wydarzenia/hackathon/",
]


def parse_html(html: str) -> list[Cand]:
    soup = BeautifulSoup(html, "lxml")
    out: list[Cand] = []
    for box in soup.select("div.event-list"):
        if "old" in (box.get("class") or []):  # past events section
            continue
        for month in box.select("div.monthsbox"):
            mname = month.select_one(".calendar-date > div")
            ytxt = month.select_one(".monthbox-year")
            mn = month_pl(mname.get_text()) if mname else None
            ym = re.search(r"(20\d\d)", ytxt.get_text()) if ytxt else None
            if not (mn and ym):
                continue
            year = int(ym.group(1))
            for row in month.select("div.tab-row"):
                if row.find_parent(class_="old"):
                    continue
                a = row.select_one("a[href]")
                title = row.select_one(".colTab.title")
                if not (a and title):
                    continue
                nums = [n.get_text(strip=True) for n in row.select(".colTab.date .num")]
                dm = [re.match(r"-?\s*(\d{1,2})\.(\d{1,2})", n) for n in nums]
                dm = [m for m in dm if m]
                if not dm:
                    continue
                try:
                    start = dt.date(year, int(dm[0][2]), int(dm[0][1]))
                    end = dt.date(year + (1 if int(dm[-1][2]) < int(dm[0][2]) else 0), int(dm[-1][2]), int(dm[-1][1])) if len(dm) > 1 else None
                except ValueError:
                    continue
                for t in title.select(".topics"):
                    t.extract()
                city = row.select_one(".colTab.city")
                typ = row.select_one(".colTab.type")
                typ_t = clean_text(typ.get_text()) if typ else ""
                city_t = clean_text(city.get_text()) if city else ""
                out.append(Cand(
                    title=clean_text(title.get_text()), url=BASE + a["href"].split("?")[0], source="crossweb",
                    start=start, end=end, location=city_t,
                    online=True if city_t.lower() == "online" else None,
                    country="PL" if city_t and city_t.lower() != "online" else None,
                    kind_hint="hackathon" if typ_t.lower() == "hackathon" else None,
                    extra={"type": typ_t}))
    return out


def parse_rss(xml_text: str) -> list[Cand]:
    out = []
    data = xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text
    # the feed occasionally contains stray control chars -> be lenient instead of failing
    root = ET.fromstring(data, parser=ET.XMLParser(recover=True))
    for it in root.iter("item"):
        title = clean_text(it.findtext("title"))
        link = (it.findtext("link") or "").split("?")[0]
        pub = it.findtext("pubDate")
        try:
            start = parsedate_to_datetime(pub).astimezone(WAW) if pub else None
        except (TypeError, ValueError):
            start = None
        if title and link and start:
            out.append(Cand(title=title, url=link, source="crossweb", start=start, location="Krak\u00f3w",
                            country="PL", summary=clean_text(it.findtext("description"), 300)))
    return out


def fetch(cfg: dict, warn) -> list[Cand]:
    found: dict[str, Cand] = {}
    errors = []
    loaded = 0
    for p in cfg.get("pages", PAGES):
        try:
            html = http(BASE + p, impersonate=True).text
            loaded += 1
            for c in parse_html(html):
                found.setdefault(c.url, c)
        except Exception as ex:  # noqa: BLE001
            errors.append(f"{p}: {ex}")
    html_count = len(found)
    try:
        xml = http(BASE + "/rss/wydarzenia/krakow/", impersonate=True).content.decode("utf-8", "replace")
        for c in parse_rss(xml):
            found.setdefault(c.url, c)
    except Exception as ex:  # noqa: BLE001
        errors.append(f"rss: {ex}")
    if loaded and html_count == 0:
        warn("HTML pages loaded but parser extracted 0 rows - markup probably changed; RSS fallback used")
    for e in errors[:3]:
        warn(e)
    if not found and errors:
        raise RuntimeError("; ".join(errors[:3]))
    return list(found.values())
