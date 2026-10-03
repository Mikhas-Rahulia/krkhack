"""Static site output (Polish UI): index.html, events.json, ICS calendars, RSS, health."""
from __future__ import annotations

import datetime as dt
import html
import json
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .sources_info import SOURCES, STATUS_PL
from .util import WAW

ROOT = Path(__file__).resolve().parents[1]
TIER_TITLES = {
    "krakow": ("W Krakowie", "Na miejscu w Krakowie (także hybrydowo z lokalizacją w Krakowie)"),
    "nearby": ("W okolicy Krakowa", "Małopolska i miasta Śląska w zasięgu 1–2 godzin"),
    "poland": ("Reszta Polski", "Warto wyjechać — albo dobra okazja, by zobaczyć inne miasto"),
    "online": ("Online", "Zdalnie, prosto z domu"),
}
DAYS = ["pon.", "wt.", "śr.", "czw.", "pt.", "sob.", "niedz."]
MONTHS = ["sty", "lut", "mar", "kwi", "maj", "cze", "lip", "sie", "wrz", "paź", "lis", "gru"]
KIND_PL = {"ctf": "CTF", "gamejam": "game jam", "hacknight": "nocne hakowanie"}
AUD_PL = {"students": "dla studentów", "pupils": "dla uczniów"}
HOST_LABELS = {"crossweb.pl": "Crossweb", "devpost.com": "Devpost", "lu.ma": "Luma", "luma.com": "Luma",
               "meetup.com": "Meetup", "dev.events": "dev.events", "gdg.community.dev": "GDG", "ctftime.org": "CTFtime",
               "devfolio.co": "Devfolio", "mlh.com": "MLH", "mlh.io": "MLH"}


def _d(s: str) -> dt.date:
    return dt.date.fromisoformat(s[:10])


def fmt_when(e: dict) -> str:
    s = _d(e["start"])
    if e.get("precision") == "month":
        return f"{MONTHS[s.month - 1]} {s.year} · termin wkrótce"
    en = _d(e["end"]) if e.get("end") else s
    t = "" if e.get("all_day") else f", {e['start'][11:16]}"
    if en == s:
        return f"{DAYS[s.weekday()]} {s.day} {MONTHS[s.month - 1]} {s.year}{t}"
    if en.month == s.month and en.year == s.year:
        return f"{s.day}–{en.day} {MONTHS[s.month - 1]} {s.year}"
    return f"{s.day} {MONTHS[s.month - 1]} – {en.day} {MONTHS[en.month - 1]} {en.year}"


def badge(e: dict) -> dict:
    s = _d(e["start"])
    if e.get("precision") == "month":
        return {"top": MONTHS[s.month - 1].upper(), "big": "?", "sub": str(s.year)}
    en = _d(e["end"]) if e.get("end") else s
    big = str(s.day) if en == s else f"{s.day}–{en.day}" if en.month == s.month else f"{s.day}→"
    return {"top": MONTHS[s.month - 1].upper(), "big": big, "sub": DAYS[s.weekday()] if en == s else str(s.year)}


def link_chips(e: dict) -> list[dict]:
    seen, out = set(), []
    for l in e.get("links", []):
        host = urlparse(l["url"]).netloc.lower().removeprefix("www.")
        if host in seen or not host:
            continue
        seen.add(host)
        out.append({"url": l["url"], "label": HOST_LABELS.get(host, host)})
    return out[:4]


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
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//krkhack//Hackathony Krakow//PL", "CALSCALE:GREGORIAN",
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
           "<title>Hackathony Kraków — nowe wpisy</title>", f"<link>{html.escape(base_url)}</link>",
           "<description>Nowo znalezione hackathony w Krakowie i okolicy</description>"]
    for e in items:
        pub = dt.datetime.fromisoformat(e.get("first_seen", dt.date.today().isoformat())).replace(tzinfo=dt.timezone.utc)
        out.append(
            f"<item><title>{html.escape(e['title'])} — {html.escape(fmt_when(e))}</title>"
            f"<link>{html.escape(e['url'])}</link><guid isPermaLink=\"false\">{e['id']}</guid>"
            f"<pubDate>{format_datetime(pub)}</pubDate>"
            f"<description>{html.escape((e.get('location') or '') + ' — ' + (e.get('summary') or ''))}</description></item>")
    out.append("</channel></rss>")
    return "".join(out)


def _ago(iso_s: str | None) -> str:
    if not iso_s:
        return "—"
    try:
        d = dt.datetime.fromisoformat(iso_s)
    except ValueError:
        return "—"
    delta = dt.datetime.now(dt.timezone.utc) - d
    h = int(delta.total_seconds() // 3600)
    return "przed chwilą" if h < 1 else f"{h} godz. temu" if h < 48 else f"{h // 24} dni temu"


def build(result: dict, outdir: Path, *, base_url: str = "") -> None:
    events, health = result["events"], result["health"]
    outdir.mkdir(parents=True, exist_ok=True)
    ref = dt.date.today()
    confirmed = [e for e in events if e["status"] == "confirmed"]
    groups = {t: [e for e in confirmed if e["tier"] == t] for t in TIER_TITLES}
    expected = [e for e in events if e["status"] == "expected"]
    for e in events:
        e["when"] = fmt_when(e)
        e["badge"] = badge(e)
        e["chips"] = link_chips(e)
        e["kind_pl"] = KIND_PL.get(e["kind"], "")
        e["aud_pl"] = AUD_PL.get(e["audience"], "")
        e["is_new"] = (ref - _d(e.get("first_seen", ref.isoformat()))).days <= 7 and e["status"] == "confirmed"
    hs = health.get("sources", {})
    sources = []
    for s in SOURCES:
        h = hs.get(s["key"], {})
        sources.append({**s, "status": h.get("status", "ok" if s["key"] in ("manual",) else "—"),
                        "status_pl": STATUS_PL.get(h.get("status", ""), "—"), "scanned": h.get("raw"),
                        "kept": h.get("kept"), "last_ok": _ago(h.get("last_ok")), "flag": h.get("flag") or ""})
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]))
    page = env.get_template("index.html.j2").render(
        groups=groups, tiers=TIER_TITLES, expected=expected, sources=sources,
        generated=health.get("generated", ""), n_confirmed=len(confirmed),
        n_krakow=len(groups["krakow"]), n_local=len(groups["krakow"]) + len(groups["nearby"]),
        n_expected=len(expected), n_sources=len(SOURCES), base_url=base_url)
    (outdir / "index.html").write_text(page, encoding="utf-8")
    slim = {"generated": result.get("generated") or health.get("generated"), "events": events}
    (outdir / "events.json").write_text(json.dumps(slim, ensure_ascii=False, indent=1), encoding="utf-8")
    physical = [e for e in confirmed if e["tier"] != "online"]
    (outdir / "krakow-hackathons.ics").write_text(make_ics(physical, "Hackathony Kraków"), encoding="utf-8", newline="")
    (outdir / "krakow-hackathons-all.ics").write_text(make_ics(confirmed, "Hackathony Kraków (z online)"), encoding="utf-8", newline="")
    (outdir / "feed.xml").write_text(make_rss(events, base_url or "./"), encoding="utf-8")
    (outdir / "health.json").write_text(json.dumps(health, ensure_ascii=False, indent=1), encoding="utf-8")
    (outdir / ".nojekyll").write_text("")
