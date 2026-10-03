"""Long-tail discovery: web search -> fetch page -> structured extraction.

 * search providers: Tavily (TAVILY_API_KEY, free tier) else keyless DuckDuckGo HTML fallback
 * extraction: schema.org JSON-LD first (free, exact), else an OpenAI-compatible LLM
   (LLM_API_KEY [+ LLM_BASE_URL, LLM_MODEL]; Gemini / GitHub Models / OpenAI / Groq all work)
 * anti-hallucination: the model must quote the sentence containing the date, and the quote must
   appear verbatim in the fetched page, and the date must parse and be in the future.
Everything degrades gracefully: no keys => keyless search + JSON-LD only; failure => warning only."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import urllib.parse
from pathlib import Path

from bs4 import BeautifulSoup

from .jsonld import events_from_html
from .model import Cand
from .util import clean_text, http, log, parse_iso, today

CACHE = Path(__file__).resolve().parents[1] / "data" / "discovery_cache.json"
SKIP_DOMAINS = ("facebook.com", "instagram.com", "linkedin.com", "x.com", "twitter.com", "tiktok.com",
                "youtube.com", "reddit.com", "pinterest.", "wikipedia.org")


# ------------------------------------------------------------------ search
def search(query: str, n: int = 8) -> list[dict]:
    key = os.getenv("TAVILY_API_KEY")
    if key:
        r = http("https://api.tavily.com/search", method="POST", headers={"Authorization": f"Bearer {key}"},
                 json={"query": query, "max_results": n, "search_depth": "basic", "topic": "general"}).json()
        return [{"title": x.get("title", ""), "url": x["url"], "snippet": x.get("content", "")} for x in r.get("results", [])]
    return _ddg(query, n)


def _ddg(query: str, n: int) -> list[dict]:
    r = http("https://html.duckduckgo.com/html/", params={"q": query, "kl": "pl-pl"})
    body = r.text
    if r.status_code == 202 or "bots use DuckDuckGo" in body:
        raise RuntimeError("DuckDuckGo bot check (datacenter IPs are blocked)")
    out = []
    for m in re.finditer(r'class="result__a" href="([^"]+)">(.*?)</a>', body, re.S):
        href = m.group(1)
        u = re.search(r"uddg=([^&]+)", href)
        url = urllib.parse.unquote(u.group(1)) if u else href
        if url.startswith("//"):
            url = "https:" + url
        out.append({"title": clean_text(m.group(2)), "url": url, "snippet": ""})
        if len(out) >= n:
            break
    return out


# ------------------------------------------------------------------ extraction
_PROMPT = """Today is {today}. Below is the text of a web page. Extract UPCOMING hackathon-type events
(hackathon, game jam, CTF, datathon, buildathon) that are held in or open to participants in Krakow, Poland
(in person in Krakow/Malopolska, or online/hybrid and open to Poland-based people). Ignore past events,
conferences without a hackathon, and anything you are not sure about.
Return ONLY JSON: {{"events":[{{"title":str,"start":"YYYY-MM-DD","end":"YYYY-MM-DD or null","location":str,
"online":bool,"evidence":"a VERBATIM quote (max 200 chars) from the page that contains the date"}}]}}.
If none, return {{"events":[]}}.

PAGE URL: {url}
PAGE TEXT:
{text}"""


_llm_failures = 0


def llm_available() -> bool:
    # after 3 consecutive failures stop burning time on a broken/blocked endpoint for this run
    return bool(os.getenv("LLM_API_KEY")) and _llm_failures < 3


def _llm(prompt: str) -> str:
    base = os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai").rstrip("/")
    r = http(f"{base}/chat/completions", method="POST",
             headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}"},
             json={"model": os.getenv("LLM_MODEL", "gemini-2.5-flash"), "temperature": 0,
                   "messages": [{"role": "user", "content": prompt}]}, timeout=90, retries=1).json()
    return r["choices"][0]["message"]["content"]


def _norm(s: str) -> str:
    return re.sub(r"\W+", " ", s.lower()).strip()


def parse_llm_events(raw: str, page_text: str, url: str, source: str = "discovery") -> list[Cand]:
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return []
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    hay = _norm(page_text)
    out = []
    for e in data.get("events", []):
        start = parse_iso(str(e.get("start") or ""))
        if not start or not e.get("title"):
            continue
        ev = _norm(str(e.get("evidence") or ""))
        if len(ev) < 12 or ev not in hay:  # hallucination guard
            log.info("discovery: dropped unverifiable event %r", e.get("title"))
            continue
        if (start if isinstance(start, dt.date) and not isinstance(start, dt.datetime) else start.date()) < today():
            continue
        out.append(Cand(title=clean_text(str(e["title"])), url=url, source=source, start=start,
                        end=parse_iso(str(e.get("end") or "")), location=clean_text(str(e.get("location") or "")),
                        online=e.get("online"), kind_hint="hackathon", summary="Found via web search (verified quote)",
                        extra={"evidence": str(e.get("evidence"))[:200]}))
    return out


def extract(url: str) -> list[Cand]:
    html = http(url, timeout=25, retries=1).text
    found = events_from_html(html, url, "discovery")
    if found:
        return found
    if not llm_available():
        return []
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "nav", "footer", "noscript"]):
        t.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()[:14000]
    global _llm_failures
    try:
        raw = _llm(_PROMPT.format(today=today().isoformat(), url=url, text=text))
        _llm_failures = 0
    except Exception:
        _llm_failures += 1
        raise
    return parse_llm_events(raw, text, url)


# ------------------------------------------------------------------ driver
def _load_cache() -> dict:
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def run(cfg: dict, warn, known_urls: set[str], extra_queries: list[str] | None = None) -> list[Cand]:
    queries = list(cfg.get("queries", [])) + list(extra_queries or [])
    max_pages = int(cfg.get("max_pages", 25))
    ttl = int(cfg.get("recheck_days", 7))
    cache = _load_cache()
    now = dt.datetime.now(dt.timezone.utc)
    out: list[Cand] = []
    fetched = 0
    total_results, failed = 0, 0
    for q in queries:
        try:
            results = search(q, int(cfg.get("results_per_query", 8)))
        except Exception as ex:  # noqa: BLE001
            failed += 1
            if failed <= 2:
                warn(f"search '{q}': {str(ex)[:120]}")
            if failed >= 3 and total_results == 0:
                break  # blocked: stop hammering
            continue
        total_results += len(results)
        for r in results:
            url = r["url"]
            host = urllib.parse.urlparse(url).netloc.lower()
            if any(d in host for d in SKIP_DOMAINS) or url in known_urls or fetched >= max_pages:
                continue
            seen = cache.get(url)
            if seen and (now - dt.datetime.fromisoformat(seen["ts"])).days < ttl:
                continue
            fetched += 1
            try:
                got = extract(url)
            except Exception as ex:  # noqa: BLE001
                warn(f"extract {url}: {ex}")
                got = []
            cache[url] = {"ts": now.isoformat(), "n": len(got)}
            out += got
    if queries and total_results == 0 and not os.getenv("TAVILY_API_KEY"):
        warn("! web search returns nothing from this network (DuckDuckGo blocks datacenter IPs) - "
             "add the free TAVILY_API_KEY repo secret to enable discovery")
    elif queries and total_results == 0:
        warn("! web search returned no results at all - check the Tavily key/quota")
    # prune cache
    cache = {u: v for u, v in cache.items() if (now - dt.datetime.fromisoformat(v["ts"])).days < 60}
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
    return out
