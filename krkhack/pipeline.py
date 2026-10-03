"""Orchestration: fetch -> normalise -> dedupe -> carry-forward -> series placeholders -> health."""
from __future__ import annotations

import datetime as dt
import difflib
import hashlib
import json
import re
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from . import discovery, series as series_mod
from .classify import audience_of, kind_of, locate
from .model import Cand
from .sources import REGISTRY
from .util import Reporter, as_date, iso, log, today

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# who wins when several sources describe the same event (title/url/summary come from the winner)
PRIORITY = ["manual", "series", "page", "ics", "devpost", "luma", "gdg", "crossweb", "ctftime",
            "mlh", "devfolio", "discovery"]
GRACE_DAYS = 14   # keep an event that vanished from sources this long (flaky parsers / paging)


def prio(sources: list[str]) -> int:
    best = 99
    for s in sources:
        base = s.split(":")[0]
        best = min(best, PRIORITY.index(base) if base in PRIORITY else 50)
    return best


# --------------------------------------------------------------------------- normalise
def slug(s: str) -> str:
    s = s.lower()
    for a, b in zip("\u0105\u0107\u0119\u0142\u0144\u00f3\u015b\u017a\u017c\u00f6", "acelnoszzo"):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


_STOP = {"hackathon", "hakaton", "hackaton", "edition", "edycja", "the", "of", "in", "w", "i", "and", "x",
         "kraków", "krakow", "cracow", "2025", "2026", "2027", "2028", "online", "ed", "vol", "powered", "by"}


def tokens(title: str) -> set[str]:
    return {t for t in re.split(r"\W+", slug(title).replace("-", " ")) if len(t) > 1 and t not in _STOP}


def normalize(c: Cand, series_list: list[dict], cfg: dict, ref: dt.date) -> dict | None:
    if not c.start or not c.title.strip():
        return None
    start = c.start
    end = c.end if c.end and as_date(c.end) >= as_date(start) else None
    pats = series_mod.patterns(series_list)
    kind = c.kind_hint or kind_of(c.title, pats)
    if not kind:
        return None
    tier, is_online = locate(f"{c.location} {c.title}", country=c.country, online=c.online)
    ser = series_mod.match(series_list, c.title)
    if ser and ser.get("tier") in ("krakow", "nearby", "poland", "online") and tier is None:
        tier = ser["tier"]
    if tier is None:
        return None
    all_day = not hasattr(start, "hour")
    return {
        "title": re.sub(r"\s+", " ", c.title).strip(), "url": c.url, "start": iso(start),
        "end": iso(end) if end else None, "all_day": all_day, "precision": "day",
        "location": c.location.strip(", "), "tier": tier, "online": bool(is_online), "kind": kind,
        "status": c.status, "summary": c.summary, "audience": audience_of(f"{c.title} {c.summary}"),
        "sources": [c.source], "links": [{"source": c.source, "url": c.url}] if c.url else [],
        "series": ser["id"] if ser else None,
    }


def end_date(e: dict) -> dt.date:
    return dt.date.fromisoformat((e.get("end") or e["start"])[:10])


def start_date(e: dict) -> dt.date:
    return dt.date.fromisoformat(e["start"][:10])


def canon_url(u: str) -> str:
    u = re.sub(r"^https?://(www\.)?", "", (u or "").lower()).split("#")[0].split("?")[0].rstrip("/")
    return u


def same_event(a: dict, b: dict) -> bool:
    if a["status"] != b["status"]:
        return False
    cu_a, cu_b = canon_url(a["url"]), canon_url(b["url"])
    if cu_a and cu_a == cu_b and abs((start_date(a) - start_date(b)).days) < 45:
        return True
    near = abs((start_date(a) - start_date(b)).days) <= 2 or (
        start_date(a) <= end_date(b) and start_date(b) <= end_date(a))
    if a.get("series") and a["series"] == b.get("series") and abs((start_date(a) - start_date(b)).days) <= 60:
        return True
    if not near:
        return False
    ta, tb = tokens(a["title"]), tokens(b["title"])
    if ta and tb and (ta <= tb or tb <= ta) and len(ta & tb) >= 1:
        return True
    return difflib.SequenceMatcher(None, slug(a["title"]), slug(b["title"])).ratio() >= 0.8


def merge(a: dict, b: dict) -> dict:
    """Merge b into a (a assumed higher priority or equal)."""
    if prio(b["sources"]) < prio(a["sources"]):
        a, b = b, a
    m = dict(a)
    m["sources"] = sorted(set(a["sources"]) | set(b["sources"]))
    seen, links = set(), []
    for l in a["links"] + b["links"]:
        if l["url"] not in seen:
            seen.add(l["url"])
            links.append(l)
    m["links"] = links
    for k in ("summary", "location", "end"):
        if not m.get(k):
            m[k] = b.get(k)
    if len(b.get("summary") or "") > len(m.get("summary") or "") + 40:
        m["summary"] = b["summary"]
    if a["all_day"] and not b["all_day"] and start_date(a) == start_date(b):
        m["start"], m["all_day"] = b["start"], False
    # a more specific geography wins (krakow > nearby > poland > online)
    order = ["krakow", "nearby", "poland", "online"]
    m["tier"] = min(a["tier"], b["tier"], key=order.index)
    m["online"] = a["online"] and b["online"]
    m["audience"] = a["audience"] if a["audience"] != "open" else b["audience"]
    m["series"] = a.get("series") or b.get("series")
    seen = [x for x in (a.get("first_seen"), b.get("first_seen")) if x]
    m["first_seen"] = min(seen) if seen else None
    return m


def dedupe(events: list[dict]) -> list[dict]:
    events = sorted(events, key=lambda e: (e["start"], prio(e["sources"])))
    out: list[dict] = []
    for e in events:
        for i, o in enumerate(out):
            if same_event(o, e):
                out[i] = merge(o, e)
                break
        else:
            out.append(e)
    return out


def collapse_recurring(events: list[dict]) -> list[dict]:
    """Weekly hack nights etc. -> only the next one, with a counter."""
    out, seen = [], {}
    for e in sorted(events, key=lambda x: x["start"]):
        if e["kind"] != "hacknight":
            out.append(e)
            continue
        key = slug(re.sub(r"\d+", "", e["title"]))[:30]
        if key in seen:
            seen[key]["more"] = seen[key].get("more", 0) + 1
        else:
            seen[key] = e
            out.append(e)
    return out


def make_id(e: dict) -> str:
    return f"{slug(e['title'])[:48]}-{e['start'][:7]}-{hashlib.sha1(canon_url(e['url']).encode()).hexdigest()[:4]}"


# --------------------------------------------------------------------------- run
def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default


def run_sources(cfg: dict) -> dict[str, dict]:
    """Run all enabled sources in parallel; never raise."""
    def one(name: str):
        scfg = cfg["sources"][name]
        rep = Reporter()
        t0 = time.time()
        try:
            cands = REGISTRY[name](scfg, rep)
            return name, {"ok": True, "cands": cands, "error": None, "warnings": rep.warnings,
                          "scanned": rep.scanned or len(cands), "secs": round(time.time() - t0, 1)}
        except Exception as ex:  # noqa: BLE001
            log.warning("source %s failed: %s", name, ex)
            return name, {"ok": False, "cands": [], "error": str(ex)[:300], "warnings": rep.warnings,
                          "scanned": 0, "secs": round(time.time() - t0, 1)}

    names = [n for n, c in cfg["sources"].items() if c.get("enabled", True) and n in REGISTRY]
    with ThreadPoolExecutor(max_workers=6) as ex:
        return dict(ex.map(one, names))


def update_health(results: dict[str, dict], kept: dict[str, int], cfg: dict, health: dict) -> dict:
    need = int(cfg.get("health", {}).get("degraded_after_runs", 3))
    srcs = health.setdefault("sources", {})
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    for name, r in results.items():
        h = srcs.setdefault(name, {"history": [], "bad_streak": 0})
        raw = r.get("scanned") if r.get("scanned") is not None else len(r["cands"])
        raw = raw or len(r["cands"])
        hist = [x for x in h["history"] if x is not None]
        med = statistics.median(hist[-10:]) if hist else 0
        r["warnings"] = sorted(r["warnings"], key=lambda w: not w.startswith("!"))  # "!" = needs a human, show first
        flagged = next((w for w in r["warnings"] if w.startswith("!")), None)
        bad = (not r["ok"]) or bool(flagged) or (med > 0 and raw == 0) or (med >= 4 and raw < 0.25 * med)
        h["bad_streak"] = h["bad_streak"] + 1 if bad else 0
        h["history"] = (h["history"] + [raw if r["ok"] else None])[-30:]
        h.update(raw=raw, kept=kept.get(name, 0), error=r["error"], warnings=r["warnings"][:5], secs=r["secs"],
                 median=med, last_run=now, flag=(flagged or "")[1:].strip())
        if r["ok"] and not bad:
            h["last_ok"] = now
        h["status"] = ("down" if not r["ok"] and h["bad_streak"] >= need else
                       "degraded" if h["bad_streak"] >= need else
                       "warning" if bad else "ok")
    health["generated"] = now
    return health


def run(cfg: dict, *, offline_cands: list[Cand] | None = None) -> dict:
    ref = today()
    series_list = series_mod.load()
    prev = load_json(DATA / "events.json", {"events": []})
    prev_events = prev.get("events", [])
    state = load_json(DATA / "state.json", {"series_last_seen": {}})
    health = load_json(DATA / "health.json", {})

    results = run_sources(cfg) if offline_cands is None else {"offline": {"ok": True, "cands": offline_cands, "error": None, "warnings": [], "secs": 0}}
    if cfg.get("series_check", True) and offline_cands is None:
        warns: list[str] = []
        sc = series_mod.check_pages(series_list, warns.append)
        results["series_pages"] = {"ok": True, "cands": sc, "error": None, "warnings": warns[:5], "secs": 0}

    def build(all_results) -> tuple[list[dict], dict[str, int], dict[str, str]]:
        evs, kept, last = [], {}, dict(state.get("series_last_seen", {}))
        for name, r in all_results.items():
            for c in r["cands"]:
                e = normalize(c, series_list, cfg, ref)
                if not e:
                    continue
                if e["series"]:  # remember the latest edition (even past ones) to time the next window
                    last[e["series"]] = max(last.get(e["series"], "0000"), end_date(e).isoformat())
                if end_date(e) < ref - dt.timedelta(days=int(cfg.get("show_past_days", 0))):
                    continue
                if start_date(e) > ref + dt.timedelta(days=int(cfg.get("horizon_days", 400))):
                    continue
                kept[name] = kept.get(name, 0) + 1
                evs.append(e)
        return evs, kept, last

    events, kept, last_seen = build(results)
    merged = dedupe(events)

    # ---- discovery (long tail), including targeted searches for series whose window is near
    dcfg = cfg.get("discovery", {})
    if dcfg.get("enabled") and offline_cands is None:
        exp = series_mod.expected_events(series_list, merged, last_seen, ref)
        look = int(dcfg.get("series_lookahead_days", 120))
        extra = [f"{x['title']} {x['start'][:4]}" for x in exp if (start_date(x) - ref).days <= look]
        y = ref.year
        queries = [q.format(year=y, next_year=y + 1) for q in dcfg.get("queries", [])]
        d_cfg = {**dcfg, "queries": queries}
        warns = []
        known = {c.url for r in results.values() for c in r["cands"]}
        try:
            found = discovery.run(d_cfg, warns.append, known, extra)
        except Exception as ex:  # noqa: BLE001
            found, warns = [], [f"discovery crashed: {ex}"]
        results["discovery"] = {"ok": True, "cands": found, "error": None, "warnings": warns[:5], "secs": 0}
        events, kept, last_seen = build(results)
        merged = dedupe(events)

    # ---- carry forward events that vanished (flaky source / paging) within the grace period
    now_iso = ref.isoformat()
    for e in merged:
        old = next((p for p in prev_events if p.get("status") == "confirmed" and same_event(p, e)), None)
        e["first_seen"] = (old or {}).get("first_seen") or e.get("first_seen") or now_iso
        e["last_seen"] = now_iso
    carried = []
    for p in prev_events:
        if p.get("status") != "confirmed" or any(same_event(p, e) for e in merged):
            continue
        if set(p["sources"]) <= {"manual", "series"}:
            continue
        if (ref - dt.date.fromisoformat(p.get("last_seen", now_iso))).days <= GRACE_DAYS and end_date(p) >= ref:
            p["stale"] = True
            carried.append(p)
    merged = dedupe(merged + carried)

    merged = collapse_recurring(merged)
    for e in merged:
        e["id"] = make_id(e)

    expected = series_mod.expected_events(series_list, merged, last_seen, ref)
    for x in expected:
        x["id"] = make_id(x)
        x["first_seen"] = x["last_seen"] = now_iso
        x["all_day"] = True
    final = sorted(merged + expected, key=lambda e: (e["status"] == "expected", e["start"], e["title"]))

    health = update_health(results, kept, cfg, health)
    state["series_last_seen"] = last_seen

    out = {"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "events": final}
    DATA.mkdir(exist_ok=True)
    (DATA / "events.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (DATA / "health.json").write_text(json.dumps(health, ensure_ascii=False, indent=1), encoding="utf-8")
    (DATA / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"events": final, "health": health, "results": results}


def load_config() -> dict:
    return yaml.safe_load((ROOT / "config.yml").read_text(encoding="utf-8"))
