import re, sys, urllib.parse, time
import requests
from curl_cffi import requests as cr

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
Q = "hackathon Kraków 2026"
qe = urllib.parse.quote(Q)

def show(name, fn):
    try:
        t0 = time.time()
        code, n, snip = fn()
        print(f"[{name}] HTTP {code} results={n} {time.time()-t0:.1f}s | {snip[:90]!r}", flush=True)
    except Exception as ex:
        print(f"[{name}] ERR {str(ex)[:120]}", flush=True)

def ddg_html():
    r = requests.get("https://html.duckduckgo.com/html/", params={"q": Q, "kl": "pl-pl"}, headers={"User-Agent": UA}, timeout=30)
    return r.status_code, len(re.findall(r'class="result__a"', r.text)), re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", r.text))[:150]

def ddg_html_curl():
    r = cr.get("https://html.duckduckgo.com/html/", params={"q": Q, "kl": "pl-pl"}, impersonate="chrome", timeout=30)
    return r.status_code, len(re.findall(r'class="result__a"', r.text)), re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", r.text))[:150]

def ddg_lite():
    r = cr.post("https://lite.duckduckgo.com/lite/", data={"q": Q, "kl": "pl-pl"}, impersonate="chrome", timeout=30)
    return r.status_code, len(re.findall(r"result-link", r.text)), re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", r.text))[:150]

def mojeek():
    r = cr.get("https://www.mojeek.com/search", params={"q": Q}, impersonate="chrome", timeout=30)
    return r.status_code, len(re.findall(r'class="title"', r.text)), re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", r.text))[:150]

def bing():
    r = cr.get("https://www.bing.com/search", params={"q": Q, "setlang": "pl"}, impersonate="chrome", timeout=30)
    return r.status_code, len(re.findall(r"<li class=\"b_algo\"", r.text)), re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", r.text))[:150]

def brave():
    r = cr.get("https://search.brave.com/search", params={"q": Q}, impersonate="chrome", timeout=30)
    return r.status_code, len(re.findall(r'class="snippet', r.text)), re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", r.text))[:150]

def crossweb_curl():
    r = cr.get("https://crossweb.pl/rss/wydarzenia/krakow/", impersonate="chrome", timeout=30)
    return r.status_code, r.text.count("<item>"), r.text[:100]

def crossweb_playwright():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(user_agent=UA)
        resp = pg.goto("https://crossweb.pl/wydarzenia/krakow/", wait_until="domcontentloaded", timeout=45000)
        pg.wait_for_timeout(8000)
        html = pg.content()
        b.close()
        return resp.status, html.count("tab-row"), pg.title() if False else re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", html))[:120]

for name, fn in [("ddg_html", ddg_html), ("ddg_html_curl", ddg_html_curl), ("ddg_lite", ddg_lite), ("mojeek", mojeek), ("bing", bing),
                 ("brave", brave), ("crossweb_curl", crossweb_curl), ("crossweb_playwright", crossweb_playwright)]:
    show(name, fn)
