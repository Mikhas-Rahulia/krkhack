"""Static site output: index.html, events.json, ICS calendars, RSS, health."""
from __future__ import annotations

import datetime as dt
import html
import json
from email.utils import format_datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .util import WAW

ROOT = Path(__file__).resolve().parents[1]
TIER_TITLES = {
    "krakow": ("In Krak\u00f3w", "On-site in Krak\u00f3w (or hybrid with a Krak\u00f3w venue)"),
    "nearby": ("Near Krak\u00f3w", "Ma\u0142opolska and the Silesian cities within about 1-2 hours"),
    "poland": ("Elsewhere in Poland", "Worth a trip, or a good excuse to visit another city"),
    "online": ("Online", "Remote events you can join from Krak\u00f3w"),
}
PL_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _d(s: str) -> dt.date:
    return dt.date.fromisoformat(s[:10])


def fmt_when(e: dict) -> str:
    s = _d(e["start"])
    if e.get("precision") == "month":
        return f"{MONTHS[s.month - 1]} {s.year} \u00b7 dates TBA"
    en = _d(e["end"]) if e.get("end") else s
    t = "" if e.get("all_day") else f" {e['start'][11:16]}"
    if en == s:
        return f"{PL_DAYS[s.weekday()]} {s.day} {MONTHS[s.month - 1]} {s.year}{t}"
    if en.month == s.month and en.year == s.year:
        return f"{s.day}\u2013{en.day} {MONTHS[s.month - 1]} {s.year}"
    return f"{s.day} {MONTHS[s.month - 1]} \u2013 {en.day} {MONTHS[en.month - 1]} {en.year}"


def _fold(line: str) -> str:
    b, out = line.encode("utf-8"), []
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80:
            cut -= 1
        out.append(b[:cut].decode("utf-8"))
        b = b[cut:]
        b = b" " + b
    out.append(b.decode("utf-8"))
    return "\r\n".join(out)


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def make_ics(events: list[dict], name: str) -> str:
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//krkhack//Krakow hackathons//EN", "CALSCALE:GREGORIAN",
             f"X-WR-CALNAME:{_esc(name)}", "X-WR-TIMEZONE:Europe/Warsaw", "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
             "X-PUBLISHED-TTL:PT12H"]
    for e in events:
        if e["status"] != "confirmed":
            continue
        s = _d(e["start"])
        en = _d(e["end"]) if e.get("end") else s
        lines += ["BEGIN:VEVENT", f"UID:{e['id']}@krkhack", f"DTSTAMP:{now}"]
        if e.get("all_day"):
            lines += [f"DTSTART;VALUE=DATE:{s:%Y%m%d}", f"DTEND;VALUE=DATE:{(en + dt.timedelta(days=1)):%Y%m%d}"]
        else:
            st = dt.datetime.fromisoformat(e["start"]).replace(tzinfo=WAW).astimezone(dt.timezone.utc)
            et = (dt.datetime.fromisoformat(e["end"]).replace(tzinfo=WAW).astimezone(dt.timezone.utc)
                  if e.get("end") and "T" in e["end"] else st + dt.timedelta(hours=3))
            lines += [f"DTSTART:{st:%Y%m%dT%H%M%SZ}", f"DTEND:{et:%Y%m%dT%H%M%SZ}"]
        desc = f"{e['summary']}\n{e['url']}" if e.get("summary") else e["url"]
        lines += [f"SUMMARY:{_esc(e['title'])}", f"LOCATION:{_esc(e.get('location') or '')}",
                  f"URL:{e['url']}", f"DESCRIPTION:{_esc(desc)}", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(l) for l in lines) + "\r\n"


def make_rss(events: list[dict], base_url: str) -> str:
    items = sorted([e for e in events if e["status"] == "confirmed" and e["tier"] != "online"],
                   key=lambda e: e.get("first_seen", ""), reverse=True)[:40]
    out = ['<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>',
           "<title>Krak\u00f3w hackathons - new listings</title>", f"<link>{html.escape(base_url)}</link>",
           "<description>Newly discovered hackathons in and around Krak\u00f3w</description>"]
    for e in items:
        pub = dt.datetime.fromisoformat(e.get("first_seen", dt.date.today().isoformat())).replace(tzinfo=dt.timezone.utc)
        out.append(
            f"<item><title>{html.escape(e['title'])} \u2014 {html.escape(fmt_when(e))}</title>"
            f"<link>{html.escape(e['url'])}</link><guid isPermaLink=\"false\">{e['id']}</guid>"
            f"<pubDate>{format_datetime(pub)}</pubDate>"
            f"<description>{html.escape((e.get('location') or '') + ' \u2014 ' + (e.get('summary') or ''))}</description></item>")
    out.append("</channel></rss>")
    return "".join(out)


def build(result: dict, outdir: Path, *, base_url: str = "") -> None:
    events, health = result["events"], result["health"]
    outdir.mkdir(parents=True, exist_ok=True)
    ref = dt.date.today()
    confirmed = [e for e in events if e["status"] == "confirmed"]
    groups = {t: [e for e in confirmed if e["tier"] == t] for t in TIER_TITLES}
    expected = [e for e in events if e["status"] == "expected"]
    for e in events:
        e["when"] = fmt_when(e)
        e["is_new"] = (ref - _d(e.get("first_seen", ref.isoformat()))).days <= 7 and e["status"] == "confirmed"
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))
    page = env.get_template("index.html.j2").render(
        groups=groups, tiers=TIER_TITLES, expected=expected, health=health.get("sources", {}),
        generated=health.get("generated", ""), n_confirmed=len(confirmed),
        n_local=len(groups["krakow"]) + len(groups["nearby"]), base_url=base_url)
    (outdir / "index.html").write_text(page, encoding="utf-8")
    slim = {"generated": result.get("generated") or health.get("generated"), "events": events}
    (outdir / "events.json").write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
    physical = [e for e in confirmed if e["tier"] != "online"]
    (outdir / "krakow-hackathons.ics").write_text(make_ics(physical, "Krak\u00f3w hackathons"), encoding="utf-8", newline="")
    (outdir / "krakow-hackathons-all.ics").write_text(make_ics(confirmed, "Krak\u00f3w hackathons (incl. online)"), encoding="utf-8", newline="")
    (outdir / "feed.xml").write_text(make_rss(events, base_url or "./"), encoding="utf-8")
    (outdir / "health.json").write_text(json.dumps(health, ensure_ascii=False, indent=1), encoding="utf-8")
    (outdir / ".nojekyll").write_text("")
