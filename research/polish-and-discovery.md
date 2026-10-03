# Polish / regional sources + zero-maintenance discovery approaches (Krakow hackathons)

Tested live on **2026-10-03** (Windows, curl.exe / Python `requests` / `curl_cffi`) from a residential IP in Poland/EU.
Probe scripts + raw samples: `D:\krkhack\research\samples-pl\`.
Out of scope (other agent): Devpost, Devfolio, DoraHacks, MLH, Luma, Meetup, Eventbrite, hackathon.com. Meetup is mentioned only where it overlaps (JSON-LD, Hackerspace Kraków).

Pricing/limits were fetched from vendor pages the same day where marked **[verified]**; **[3rd-party]** = only seen in secondary sources; **[not verified]** = could not confirm.

---

## 0. Headline findings

1. **Truly upcoming, attendable Krakow hackathons are scarce right now** (Oct 2026): HackYeah is happening *today/tomorrow*; the rest are niche (AGH AI-in-Pharma 25 Oct, GrowUp online + Krakow final Jan 2027, a school-only Małopolska one). Historical cadence on Crossweb is ~5–8 Krakow hackathons/year. So "plenty to attend" needs (a) a Poland-wide + online tier, and (b) a "recurring series" tracker, not only a Krakow filter.
2. **Crossweb.pl is the single best Polish source**: it has a Krakow city list, a keyword search that returns 330 hackathon-related rows (past + future, all cities, with city + type columns), and RSS. BUT it sits behind a Cloudflare TLS-fingerprint challenge: `curl.exe` and `curl_cffi(impersonate="chrome")` get 200; `requests`, `httpx`, Node `fetch` get **403 even with a Chrome User-Agent**. Its event pages have **no schema.org Event JSON-LD**.
3. **Search + LLM discovery found 3 relevant events that Crossweb's Krakow list did not have** (AGH AI in Pharma hackathon, the Małopolska vocational hackathon, GrowUp's Krakow final). This is the strongest argument for the "generic discovery" layer.
4. **Most "obvious" Polish sites are useless for hackathons**: evenea.pl, biletyna.pl, goout.net (culture/ticketing/trainings: 0 hackathon hits), konfeo.com (registration SaaS, no public event index), krakow.pl (no calendar/RSS), justjoin.it/nofluffjobs (no events section), several domains don't exist (hackathony.pl, geekgirlscarrots.pl didn't resolve from here) or are parked (hackathon.pl is for sale).
5. **Source rot is real and already visible**: `krakhack.info` (AI KrakHack, WSEI) currently returns a Railway "Forbidden… DNS not pointing" error; `startupkrakow.pl` is "under construction"; `krakow.pl/kalendarium` 404. A zero-maintenance design must assume every per-site scraper will die.
6. **Search API landscape changed**: Bing Search API is retired (11 Aug 2025); Google Programmable Search JSON API is closed to new customers; Brave no longer has a truly free tier (needs card, $5 credit/month). Realistic free options: **Tavily (1,000 credits/mo, no card)**, **Exa ($10 free credits/mo)**, **Serper (2,500 one-time)**, **SerpApi (250/mo)**, Brave ($5 credit/mo ≈ 1,000 queries, card on file).

---

## 1. Source-by-source results

Fragility: 1 = rock solid, 5 = breaks constantly. "Yield" = items relevant to *Krakow hackathons* right now.

### 1.1 Polish event sites

| # | Source | Working endpoint(s) | Format | Krakow / hackathon filter | Yield now | Fragility | v1? |
|---|---|---|---|---|---|---|---|
| 1 | **Crossweb.pl – keyword search** | `https://crossweb.pl/wyszukiwarka/?fraza=hackathon` (also `hakaton`) | HTML (server-rendered rows: date, title, city, type, cost) | keyword yes; city/type are *columns* → filter client-side. Path filters like `/wydarzenia/hackathon/krakow/` silently redirect to `/wydarzenia/krakow/` (ignored) | 330 rows (all cities, 2019→2027), 259 typed "Hackathon". Krakow+nearby historically: 94 rows. Future Krakow: HackYeah; future elsewhere: Warsaw Demo Day, Solana Warsaw Build Station, GrowUp (Online), WUD Szczecin | **4** (Cloudflare TLS fingerprint; HTML selectors `div.tab-row`, `colTab city/type`; datacenter-IP behaviour untested) | **Yes** |
| 2 | **Crossweb.pl – Krakow city list** | `https://crossweb.pl/wydarzenia/krakow/` | HTML, 29 rows (3 months ahead + KotlinConf Apr 2027) | Krakow yes; type column ("Hackathon") client-side | 1 hackathon (HackYeah) + 23 "Spotkanie"/5 "Konferencja" incl. DevFest 10 Oct, JDD 20–21 Oct, Test Dive 16 Oct, Nighthack (Fridays) | 4 | **Yes** |
| 3 | **Crossweb.pl – RSS** | `https://crossweb.pl/rss/wydarzenia/krakow/` (also `/rss/` global, `/rss/wydarzenia/<city>/`). Type slugs (`/rss/wydarzenia/hackathon/`) return an **empty** channel | RSS 2.0 (10 KB, ~15–20 items, `pubDate` = event date, description is double-escaped HTML, charset mojibake if not decoded as UTF-8) | city yes, type no | Same as list but only nearest events, no type field → needs keyword filter | 3 (same Cloudflare gate; only curl-class TLS passes) | Yes as backup |
| 4 | Crossweb event page | e.g. `/wydarzenia/hackyeah-2026/` | HTML; has labelled fields (Typ wydarzenia, Data, Miasto, Miejsce, Adres, Strona www, Opis) | n/a | – | 3 | for detail enrichment |
| 5 | **allevents.in** (global aggregator) | `https://allevents.in/krakow/RSS` ; HTML `…/krakow/hackathons` is SEO text only | RSS (100 items, 87 KB) | city only; no category in feed | 1 hit: HackYeah (title-grep). Mostly culture/nightlife | 3 | optional |
| 6 | **dev.events** | `https://dev.events/rss.xml` (global), `https://dev.events/EU/PL/Krakow` and `/EU/PL` (HTML + **JSON-LD Event**, 8 / 29 events), `https://dev.events/hackathons` (32 JSON-LD events, global) | RSS + JSON-LD | country/city pages yes; hackathon page has no country filter | Hackathons page: **0** Poland. PL page: Krakow conferences – DevFest 10 Oct, PLNOG 15 Oct, JDD 20 Oct, 22nd Linux Autumn 23 Oct, PDUG 19 Nov, Update Conf Krakow Jun 2027. Good for *conferences*, not hackathons | 2 | Maybe (conference side-feed) |
| 7 | **GDG Krakow (Bevy)** | `https://gdg.community.dev/api/event_slim/for_chapter/578/?status=Live&fields=title,start_date,url,…&page_size=20` (chapter id 578 in page `Globals.chapter_id`) | **Clean JSON API, no auth** (68 past + 1 live) | per chapter | DevFest Kraków 10 Oct only; 0 hackathons. Event pages also carry JSON-LD Event | 2 | Optional; same API works for every GDG/Bevy chapter in Poland |
| 8 | Evenea.pl | `https://evenea.pl/wydarzenia/krakow`, `/wydarzenia/it-i-nowe-technologie/krakow` (paging `?p[page]=2&p[limit]=35`) | HTML, no JSON-LD, no feed; `robots.txt` = 404 | city + category yes; no keyword search URL found (`/szukaj` 404) | **0** hackathon mentions on IT/Krakow pages (paid trainings, HR conferences) | 3 | No |
| 9 | Konfeo.com | `https://www.konfeo.com/pl/` is marketing for registration SaaS; no public event index (event URLs `/event/view/` are disallowed in robots, `/pl/search` 404) | – | – | 0 | – | No |
| 10 | Biletyna.pl | `https://biletyna.pl/Krakow` (HTML 377 KB; culture/theatre/concerts) | HTML | city yes | 0 hackathon hits | 3 | No |
| 11 | GoOut.net | HTML `/pl/krakow/events/`; JSON `https://goout.net/services/entities/v1/events?languages[]=pl&keywords=hackathon` works (63 KB) but **ignores `keywords`**, returns Czech/Polish concerts | JSON (undocumented) | no usable filter | 0 | 4 | No |
| 12 | hackathon.pl / hackathony.pl | `hackathon.pl` redirects to aftermarket.pl (domain for sale); `hackathony.pl` NXDOMAIN | – | – | none exist | – | No |
| 13 | justjoin.it / nofluffjobs | `justjoin.it/events` 404; `justjoin.it/blog`, `nofluffjobs.com/pl/log/` are blogs, 0 hackathon mentions | – | – | 0 | – | No |
| 14 | Geek Girls Carrots, Sektor 3.0 | `geekgirlscarrots.pl`, `ggc.org.pl`, `sektor3-0.com(.pl)` – **DNS did not resolve** (curl exit 6; may be my guess at the domain being wrong) | – | – | not testable | – | No (not verified) |
| 15 | Startup Poland / SpotData / StartUp Kraków | `startuppoland.org` (news/reports; no events list), `spotdata.pl` (analysis), `startupkrakow.pl` = "under construction" | HTML | – | 0 | – | No |
| 16 | krakow.pl city calendar | `https://www.krakow.pl/kalendarium`, `/rss`, `/kalendarz_wydarzen` all 404 (generic 404 page) | – | – | 0 | – | No |
| 17 | malopolska.pl | `https://www.malopolska.pl/kalendarium` (HTML 160 KB), `https://www.malopolska.pl/rss.xml` = **news only**, links malformed (`%3Ca href…`). Search surfaced a kalendarium entry for HackYeah ("Małopolska już po raz piąty Regionem Gospodarzem") | HTML / RSS | – | indirect | 4 | No |
| 18 | Krakowski Park Technologiczny | `https://www.kpt.krakow.pl/dzieje-sie/?category=wydarzenie` (HTML) – only generic "organizujemy hackathony" text; 0 concrete | HTML | – | 0 | 3 | No |
| 19 | Hackerspace Kraków | `hackerspace-krk.pl` (static, no events); events live on Meetup (`/hackerspacekrakow/`, JSON-LD) and Crossweb | – | – | Nighthack every Friday (hack/solder night; borderline "hackathon") | – | via Meetup/Crossweb |
| 20 | krakow.dlastudenta.pl | `/studia/wydarzenia/` HTML list; 0 hackathon mentions on list page (Kościuszkon 2026 entry exists but wasn't on the first page) | HTML | – | 0–low | 3 | No |
| 21 | Hackathon organiser sites | `hackyeah.pl` (HTML, no JSON-LD; `/pl/faq/`), `tauronarenakrakow.pl/event/hackyeah-2026/`, `growuphackathon.pl`, `aiinpharma.pl/hackathon-2026/`, `fpgahackathon.com` (2026 edition over; "2027 notification signup"), `visadatasprint.com` (29–30 Sep, over) | HTML | – | per-event | – | via discovery (LLM) not per-site scrapers |

### 1.2 Universities / student orgs (feeds)

| Source | Result |
|---|---|
| AGH (`agh.edu.pl/aktualnosci`, `/wydarzenia`) | HTML only; `/rss` 404; no hackathon text on landing pages. Faculty news (e.g. `eaiib.agh.edu.pl`) *does* announce the AI-in-Pharma hackathon but is only discoverable via search |
| UJ (`uj.edu.pl`) | `/wydarzenia`, `/rss` → 404 "Status" page; `wydarzenia.uj.edu.pl` no DNS |
| PK (`pk.edu.pl`) | Joomla HTML; article pages for Kościuszkon 2026 and Visa Datasprint exist (reachable by search, not by feed) |
| UEK (`uek.krakow.pl`) | landing page only; news path 404 |
| WSEI "AI KrakHack" (`krakhack.info`) | **Broken now** (Railway error). Edition held 27–28 Mar 2026. Good example of why per-site scrapers rot |
| ACM/IEEE AGH student chapters | `acm.agh.edu.pl`, `ieee.agh.edu.pl` did not resolve. Student circles use Facebook/LinkedIn/Discord instead |
**Verdict:** no usable university feeds. Treat universities as *discovered-by-search* only.

### 1.3 Aggregator-ish / curated lists
* `laczymybiznes.pl/hackathony-i-konferencje-technologiczne-w-polsce-2026/` – SEO listicle with **wrong facts** (says HackYeah "September 2026, 48 h"; real: 3–4 Oct, 24 h). Do not use as a source; LLM extraction from such pages needs a "must have an official URL + date confirmed on 2nd source" rule.
* `hackalist.org` (global, mostly US), `confs.tech` (conferences, JS app) – no Poland value.

---

## 2. Community channels – feasibility only

| Channel | Scrapable / API? | ToS / practical notes | Verdict |
|---|---|---|---|
| **Telegram public channels** | `https://t.me/s/<channel>` returns server-rendered HTML preview of the last ~20 posts (tested: 200, 146 KB for a public channel). Bot API cannot read channels unless the bot is admin | Light scraping of public preview tolerated; no official ToS-safe bulk reading. Also needs a known channel list (no Polish Krakow hackathon channel found) | Feasible *if* you find 1–3 good channels; low priority |
| **Telegram as output** | Bot API `sendMessage` is free, simple | Official | **Use as delivery channel** |
| **Discord** | No API to read servers you don't belong to; user-token scraping = ToS violation (ban). Invite metadata endpoint works (`/api/v10/invites/<code>` → 200 JSON, guild name/counts only) | Bot must be invited by server admin | **Not feasible** for discovery |
| **Slack** | Workspaces are private; no public API | – | Not feasible |
| **Facebook groups/events** | `facebook.com/events/search` → HTTP 400 for anonymous; Graph API event search removed years ago; scraping prohibited by ToS | Student circles & many Krakow hackathons announce here only | Not feasible (indirectly covered by web-search snippets) |
| **LinkedIn** | Anonymous event search → login wall (200 login page). Official API has no public events search; scraping prohibited | But **LinkedIn posts appear in web search results** with full text (e.g. AI Krak Hack recap) – use the search layer instead | Not directly feasible |
| **Reddit** | `https://www.reddit.com/r/krakow/search.rss?q=hackathon&restrict_sr=1&sort=new` → 200 Atom (works, returned a 2024 ZK Hack post). `.json` endpoints 403 | Reddit API terms require registration for automated use; RSS lightly used OK | Cheap optional signal, low yield |
| **Bluesky** public search API | 403 from this IP without auth | – | skip |
| **Mastodon** | `mastodon.social/api/v1/timelines/tag/hackathon` 200 JSON (global, mostly irrelevant); `v2/search` needs auth | – | skip |

---

## 3. Generic discovery approaches (no per-site maintenance)

### 3.1 Search-API discovery (queries like `hackathon Kraków 2026`)

Live proof of concept (no API key needed): DuckDuckGo HTML endpoint returned good results for the first query (HackYeah ×4, Visa Datasprint, Hacknarök, FPGA Hackathon, a listicle) and then served a **captcha on the next 3 queries** → keyless scraping is unusable for cron. The Cursor `WebSearch` tool (real search backend) additionally surfaced AI-in-Pharma, GrowUp, the Małopolska vocational hackathon, AI KrakHack (past), Kościuszkon (past) – i.e. good recall, mixed with past events and listicles → needs LLM filtering + date logic.

| Provider | Free tier today | Paid | Limits | Status |
|---|---|---|---|---|
| **Tavily** | **1,000 API credits/month, no card** [verified tavily.com/pricing]; resets 1st of month | $0.008/credit pay-as-you-go; a monthly plan with 4,000 credits exists (its $ price did not render in my fetch – not verified) | search = 1 credit (basic) [docs, not re-verified] | Best fit: LLM-oriented, returns cleaned page content, supports `include_domains`, `time_range`, `country` |
| **Exa** | **$10 free credits at signup and refilled to $10 on the 1st of each month**, ≈2,500 instant searches, no card [verified exa.ai/pricing]. Complete onboarding for extra one-time $10 | Search $4–7 / 1k requests; Contents $1/1k pages; **Monitors $15/1k requests ("scheduled searches that surface new events")**; Deep search $12–15/1k | – | Excellent semantic queries ("hackathon in Krakow in next 3 months"); Monitors is literally a managed "new-event watcher" |
| **Brave Search API** | **No longer fully free**: $5 credit/month ≈ 1,000 requests, **credit card required** (anti-fraud), set spending cap = credit [verified brave.com/search/api + community]; "Existing free plans unaffected" | $5 / 1k requests; 50 QPS (Search plan) | rate-limit headers show e.g. 1 rps / 15,000 per month on some plans | Good quality, independent index, but card on file |
| **Serper.dev** | 2,500 free queries on signup, no card (one-time, 6-month validity) [3rd-party, serper.dev/pricing 404 per sources] | $50 / 50k credits ($1/1k) | 50 QPS | Cheap Google SERP JSON; prepaid, no subscription |
| **SerpApi** | **250 searches/mo** free [verified serpapi.com/pricing] | $25/mo for 1,000; $75/mo 5,000 | 50/hr on free | Expensive per query |
| **Google Programmable Search JSON API** | 100/day free **but closed to new customers**; existing customers must migrate by 1 Jan 2027 [verified developers.google.com] | $5/1k | – | **Don't use** |
| **Bing Web Search API** | **Retired 11 Aug 2025** [verified MS Learn]. Replacement "Grounding with Bing" $14/1k, Azure-only | – | – | **Don't use** |
| **Gemini "Grounding with Google Search"** | Paid tier only: 5,000 free grounded prompts/month then $14/1k [verified ai.google.dev pricing]; not on free tier for 3.5 Flash-Lite | – | – | Optional if already on paid Gemini |
| DuckDuckGo HTML | free, no key | – | captcha after ~1 query from same IP | ToS-grey, unreliable |

**Budget math for the intended workload** (≈ 10 queries/day: `hackathon Kraków {month}`, `hakaton Kraków`, `hackathon Polska online`, `Małopolska hackathon rejestracja`, a handful of `site:` queries) = ~300/month → fits **Tavily free (1,000)** or **Exa free ($10/mo)** with big margin. Use two providers as primary/fallback so one API change doesn't kill discovery.

Caveats: search results mix past events and SEO listicles with errors (laczymybiznes.pl); results must be date-filtered and deduplicated against official-site facts.

### 3.2 LLM extraction from arbitrary pages

Measured stripped-text sizes (nav/script removed): hackyeah.pl home ≈ 425 tokens, Tauron event page ≈ 870, AI-in-Pharma page ≈ 900, Crossweb event page ≈ 430, Crossweb Krakow list (29 rows) ≈ 1,850. So **~1,000 input tokens/page is realistic**; even budgeting 6,000 tokens in + 400 out per page:

| Model (price/1M in / out) | 30 pages/day | 100 pages/day |
|---|---|---|
| Gemini 3.5 Flash-Lite ($0.30 / $2.50) [verified ai.google.dev] | ~$2.5/mo | ~$8.4/mo |
| GPT-5 mini ($0.25 / $2.00) [verified GitHub Copilot models table] | ~$2.1/mo | ~$6.9/mo |
| GPT-5.4 nano ($0.20 / $1.25) [same table] | ~$1.5/mo | ~$5.1/mo |
| Gemini 3.8 Flash ($0.75 / $3.75 promo until 31 Dec 2026, then 2×) | ~$5.4/mo | ~$18/mo |

With realistic ~1.5k tokens/page the bill is **< $1–2/month**, and often **$0**:
* **Gemini API free tier**: Flash-Lite/Flash have "Free of charge" input+output on the Free tier (content used to improve Google products; exact RPM/RPD only visible in AI Studio – **[not verified numerically]**).
* **GitHub Models** free via `GITHUB_TOKEN`/PAT: low-tier models (gpt-4.1-mini) ≈ 15 RPM / 150 RPD, **8,000 input / 4,000 output tokens per request** [verified github/docs]; gpt-5-mini class models only 12–20 RPD on paid Copilot plans, not available on Free. Enough for ~100 page extractions/day with strict truncation; commercial-use terms unclear.
Use structured output (JSON schema: `name, start, end, city, venue, online, url, registration_deadline, is_hackathon, confidence, evidence_quote`) and **require an evidence quote + official URL**; drop anything lacking a parsable date.

Not run end-to-end here (no API keys available in this sandbox) – cost is computed (`llm_cost_estimate.py`), extraction quality is **not measured**.

### 3.3 schema.org Event JSON-LD from arbitrary event pages

Probe (`jsonld_probe.py`) on 8 real pages relevant to Krakow hackathons:

| Page | JSON-LD Event? |
|---|---|
| hackyeah.pl | no |
| crossweb.pl event pages (HackYeah, DevFest) | no (only Organization/WebSite) |
| gdg.community.dev event page | **yes** (name, start/end with TZ, venue) |
| meetup.com find/group pages | **yes** (12 events on search page; Hackerspace group 4) |
| dev.events city/country pages | **yes** (29 events on PL page, PostalAddress included) |
| spaceappschallenge.org, evenea.pl, konfeo.com | no |

⇒ JSON-LD is available on the *platforms* (Meetup, Bevy/GDG, Luma, Eventbrite, dev.events) but **not on the Polish sites and organiser microsites that matter most** (≈25–35% of pages). Use it as a free first pass (zero LLM cost) with LLM fallback, not as the only mechanism.

### 3.4 Hosting + cron (GitHub Actions + Pages / Cloudflare Pages)

* **GitHub Actions**: free & unlimited minutes for **public repos** on standard runners; private repos: 2,000 min/month on Free plan [verified docs.github.com]. A daily 3-minute job ≈ 90 min/month — free either way.
* **GOTCHA for "zero maintenance"**: in public repos scheduled workflows are **auto-disabled after 60 days without repository activity**, and cron runs can be delayed/dropped at the top of the hour [verified]. Mitigation (documented pattern): have the workflow *commit its own data file every run* (counts as activity) and/or run a weekly keep-alive job that calls `PUT /repos/{o}/{r}/actions/workflows/{id}/enable` (re-enabling resets the timer). Pick odd minutes (e.g. `17 5 * * *`).
* **GitHub Pages** for the static site/ICS/RSS (soft 1 GB site / 100 GB-month bandwidth – **[not re-verified]**) or **Cloudflare Pages** free: unlimited static requests, 500 builds/month, 20,000 files, 25 MiB/file [verified developers.cloudflare.com/pages/platform/limits]. Both are plenty for a JSON + ICS + RSS file.
* Cloudflare *Workers cron triggers* are an alternative scheduler with no 60-day rule (**[not verified]** here).
* Crossweb from Actions: **untested** – its Cloudflare gate may challenge datacenter IPs even with a good TLS fingerprint. Design must tolerate that (fallback to search+LLM).

### 3.5 Delivery: ICS, RSS, Telegram, email

* **ICS**: static `krkhack.ics` file on Pages; Google Calendar/Apple Calendar/Outlook subscribe by URL and poll (Google can take 12–24 h to refresh – known behaviour, **[not verified today]**). Use stable `UID`s (hash of canonical URL) so updates/cancellations modify rather than duplicate; add `VALARM` for registration deadlines. This is the most passive channel – set once, never opened again.
* **RSS/Atom**: static `feed.xml` (new/changed events only, `guid` = UID).
* **Telegram**: Bot API `sendMessage` to a private chat/channel – free, one `curl` in the workflow; weekly digest + "new event" pings [Telegram Bot API docs fetched; free, rate limit ~1 msg/s per chat – standard].
* **Email**: GitHub Actions + any SMTP/Resend/Brevo free tier, or simply let the user subscribe to the RSS via a free feed-to-email service. Lowest priority.

---

## 4. Recommended architecture (zero-maintenance, self-healing)

```
 ┌─────────────── GitHub Actions (public repo, cron daily 05:17 UTC + weekly keep-alive) ───────────────┐
 │ 1. COLLECT (all adapters emit the same candidate schema; each wrapped in try/except + health record)  │
 │    A. "Structured" adapters (cheap, deterministic, may die):                                          │
 │         crossweb search+Krakow list (curl_cffi chrome) · Meetup/Luma/Devpost/etc (other agent)        │
 │         dev.events PL JSON-LD · GDG Bevy API · allevents RSS (optional)                              │
 │    B. "Discovery" adapter (the safety net, never "breaks"):                                           │
 │         Tavily (+Exa fallback) × ~8 queries PL/EN × "Kraków|Małopolska|Polska online|hackathon|hakaton"│
 │         → fetch top URLs (curl_cffi) → JSON-LD Event if present else strip→LLM extract (Gemini Flash-Lite free tier)│
 │ 2. NORMALISE + FILTER: parse dates (TZ Europe/Warsaw), drop past events, geo-tag (Krakow ≤ 100 km /     │
 │    online / Poland), is_hackathon score, require official URL                                          │
 │ 3. DEDUPE: canonical URL, else fuzzy (normalised title + date ±1 day + city); keep best source; keep   │
 │    `sources[]` for provenance; stable UID = hash(canonical key)                                        │
 │ 4. VERIFY: for new/changed events re-fetch official URL, LLM confirms {dates, location, hackathon?}    │
 │    ("trust but verify" – listicles lie)                                                                │
 │ 5. SELF-HEAL / HEALTH: per-source record in data/health.json {last_ok, items, expected_min, schema_ok}; │
 │    canary assertions (e.g. crossweb Krakow list must return ≥10 rows; HackYeah-like known item present);│
 │    3 consecutive failures ⇒ mark source "degraded", widen discovery queries (Tavily site:domain +      │
 │    LLM extraction of that domain's /events page), open ONE GitHub issue / Telegram alert (rate limited)│
 │ 6. SERIES WATCHLIST: from Crossweb history infer recurring editions (Hackathon dla Małopolski Jun+Nov, │
 │    Design+Tech Nov, EIT Health i-Days Oct, FPGA Hackathon Apr/May, Cassini Nov, AI Krak Hack Mar,     │
 │    Kościuszkon May, HackYeah Oct, Space Apps Oct/Nov) → targeted search "<series> 2027" when its slot  │
 │    approaches; show as "expected, date TBA"                                                           │
 │ 7. PUBLISH: commit data/events.json (this commit also resets the 60-day cron timer) →                  │
 │    Pages: index.html (static, JSON-driven), krakow-hackathons.ics, feed.xml                           │
 │    NOTIFY: Telegram bot weekly digest + "new event" ping; email optional                               │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

Design principles
* **Two layers**: structured adapters give precision & cheap volume; the search+LLM discovery layer gives recall and *replaces any adapter that dies*. Never depend on a single scraper.
* **Fetch layer**: wrap `curl_cffi` (chrome impersonation) — needed for Crossweb; plain `requests` fails there.
* **Everything is data, not code**: query lists, domain allow/deny lists and series watchlist live in YAML so the "maintenance" is editing a text file, not code.
* **Cost**: ≈ $0/month (Tavily/Exa free tiers + Gemini/GitHub Models free tier + free hosting). Worst realistic paid case < $5/month.
* **Poland-wide + online tier** so the feed isn't empty between Krakow events; label with distance/online.
* **Compliance**: honour robots.txt (Crossweb allows `*`; only specific bots restricted), 1–2 req/s, cache by ETag, keep the user-agent honest where the site tolerates it, link back to sources; no Facebook/LinkedIn/Discord scraping.

---

## 5. Concrete Krakow(-ish) hackathons found (as of 2026-10-03)

| Name | Date | Where | URL | Notes |
|---|---|---|---|---|
| **HackYeah 2026** (12th ed., 24 h) | **3–4 Oct 2026** (started 10:00 today) | TAURON Arena Kraków | https://hackyeah.pl/ | Biggest on-site hackathon in Europe; 18+; FAQ says applications closed 15 Jul → likely sold out/closed (unverified) |
| **Studencki Hackathon AI in Pharma 2026** | **25 Oct 2026** | AGH campus, Pawilon B-1, Kraków | https://www.aiinpharma.pl/hackathon-2026/ | Free registration, limited spots, English, engineering students; run with AWS/AGH |
| **GrowUp Hackathon 2026** | register **by 20 Oct**; online Nov–Dec; **live final in Kraków Jan 2027** | Online + Kraków | https://growuphackathon.pl/ | Solo or ≤5 people (Crossweb lists it as "Online", 20 Oct) |
| "Mobilna pomoc – prosty robot ratunkowy" | 1–2 Dec 2026 (apply 2 Oct–1 Nov) | EXPO Kraków | https://malopolskauczy.pl/festiwal-uczelni/hackathon | **Vocational secondary-school students from Małopolska only** – likely not eligible |
| Nighthack (Hackerspace Kraków) | Fridays: 9, 23, 30 Oct; 6, 13, 27 Nov; 4, 11, 25 Dec … 20:00 | Limanowskiego 46/LU1, Kraków | https://www.meetup.com/hackerspacekrakow/ | Open hack/solder night, not a competition |
| NASA Space Apps Challenge 2026 | 14–15 Nov 2026 | Poland local events (Stalowa Wola confirmed); **Krakow not confirmed** (2024 was at AGH) | https://www.spaceappschallenge.org/2026/ | Local-events list is JS-rendered; check manually |
| Poland-wide/near: Solana Warsaw Build Station (6–13 Oct), Warsaw Demo Day (13 Oct), WUD Szczecin night hackathon (17–18 Oct), Colosseum Hackathon (online, to 13 Oct) | | | via Crossweb | Warsaw/Szczecin are ~2.5 h train / flight from Krakow |

Already finished (useful as recurrence signals): Visa Datasprint (29–30 Sep, Kraków), AI KrakHack (27–28 Mar), Kościuszkon (9–10 May, PK), Hackathon dla Małopolski (30–31 May), Software Mansion × Gemini (28 Mar), Hacknarök (18–19 Apr), FPGA Hackathon 2026.

---

## 6. What failed / could not be verified (honesty list)

* Crossweb from GitHub Actions/datacenter IPs – untested; Cloudflare may block.
* No LLM or search-API keys available → extraction quality, Tavily/Exa/Brave result quality not measured with the real APIs (pricing verified, behaviour inferred from the keyless DDG + Cursor WebSearch tests).
* Brave free-tier exact monthly request cap beyond "$5 credit"; Serper pricing page (404 per secondary sources); Gemini free-tier RPM/RPD numbers; GitHub Pages bandwidth numbers; ICS client refresh intervals; Cloudflare Workers cron behaviour.
* Domains that did not resolve (could be wrong domain guesses): geekgirlscarrots.pl, ggc.org.pl, sektor3-0.com, acm.agh.edu.pl, ieee.agh.edu.pl, hackathondlamalopolski.pl, wydarzenia.uj.edu.pl, wi.pk.edu.pl.
* NASA Space Apps Kraków 2026 local event: Local Events page is JS-rendered; not confirmed either way.
* Konfeo, Evenea search endpoints: no usable public keyword search found (evenea `/szukaj` 404, konfeo `/pl/search` 404); a hidden API may exist.

## 7. Files in `samples-pl/`

`probe_crossweb.py` (shows the 403s), `cf_fingerprint_test.py` (client matrix), `crossweb_extract.py` + `crossweb_hackathons.json` (working Crossweb extractor via curl_cffi), `parse_cw_list.py`, `goout_probe.py`, `gdg_probe.py` + `gdg_Live.json`, `jsonld_probe.py`, `devevents_allevents.py`, `ddg_probe.py`, `batch_probe.py` + `urls1.txt`/`urls2.txt`, `llm_cost_estimate.py`, `upcoming_krakow_hackathons_found.json`, plus raw HTML/RSS samples (`cw_rss_krakow.xml`, `allevents_rss.xml`, `devevents_rss.xml`, `malop_rss.xml`, …).
