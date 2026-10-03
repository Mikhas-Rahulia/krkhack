# Global/English hackathon platforms - live test report (Krakow, PL)

Tested: **Sat 3 Oct 2026**, from a Krakow IP (Windows, Python `requests` / `curl.exe`). All results below are from real HTTP calls made today.
Re-runnable probe: `research/samples/probe_all.py`. Raw samples: `research/samples/*.json`.

## TL;DR

* **Not one of these global platforms currently lists an upcoming Krakow hackathon.** Over the last 12 months (Oct 2025 - Oct 2026) only **2** Krakow hackathons were found anywhere (both on Devpost): *Blockchain Hack Krakow* (28-29 Mar 2026) and *Hacknarok* (18-19 Apr 2026). Both are over.
* Global platforms are a **thin supplement** for Krakow. The Polish-local sources (AGH/Hacknarok, university pages, Facebook, hackathon organisers' own sites) will carry most of the load. Use global ones mainly for (a) online hackathons open to everyone and (b) catching the occasional Krakow event.
* **Best v1 sources:** Devpost JSON API (stable, no auth), Luma discover API (lat/lon query, no auth), Meetup `gql2` GraphQL (works unauthenticated, fragile ToS), MLH (Inertia JSON in page; zero Poland ever, only useful for "Global Hack Week"/digital events).
* **Skip:** hackathon.com (stale), Hackalist/hackathons.io (dead), Unstop (India-only), Eventbrite (keyword filter doesn't work; no real hackathons), DoraHacks (no API found), Kaggle (auth + captcha).

---

## 1. Summary table

| # | Platform | Working endpoint (no auth) | Krakow filter? | Krakow now | Krakow past 12 mo | Fragility (1-5) | v1? |
|---|---|---|---|---|---|---|---|
| 1 | **Devpost** | `GET https://devpost.com/api/hackathons?search=krakow&per_page=50` | `search` only (matches title + venue text; `location` param ignored) | 0 | 2 | 2 | **Yes** |
| 2 | **Luma** | `GET https://api.lu.ma/discover/get-paginated-events?latitude=50.0647&longitude=19.945&pagination_limit=50` | Yes (lat/lon). Krakow is not a "discover place" | 0 hackathons (8 events nearby, none hackathon) | unknown (API shows future only) | 3 | **Yes** |
| 3 | **Meetup** | `POST https://www.meetup.com/gql2` `eventSearch(filter:{lat,lon,radius,query})` | Yes (lat/lon/radius); `query` is fuzzy | 0 real hackathons | unknown | 4 (ToS/anti-bot) | Maybe (low priority) |
| 4 | **MLH** | `GET https://www.mlh.com/seasons/2027/events` -> `<script data-page="app">` JSON | No location filter; filter `venueAddress.country=="PL"` client-side | 0 (never any PL event in seasons 2021-2027) | 0 | 2 | Yes, for digital/online events only |
| 5 | **Devfolio** | `POST https://api.devfolio.co/api/search/hackathons` `{"type":"application_open","from":0,"size":100}` | Fields `city`,`country`; client-side filter | 0 | 0 (last: ZK Hack Krakow, 17 May 2024) | 2 | Optional (India-centric) |
| 6 | **Eventbrite** | HTML `https://www.eventbrite.com/d/poland--krak%C3%B3w/hackathon/` (JSON-LD ItemList + `__SERVER_DATA__`) | Location yes; **keyword "hackathon" not enforced** (falls back to all Krakow events) | 0 hackathons | 0 | 4 | No |
| 7 | **hackathon.com** | HTML `https://www.hackathon.com/city/poland/krakow` (+ `/past`) | URL-based city page | 0 ("no upcoming hackathons found") | 0 (newest Krakow entries are 2018-2022 and mostly Eventbrite-imported) | 3 | No (stale) |
| 8 | **Lablab.ai** | HTML `https://lablab.ai/ai-hackathons` (RSC payload in page) | No (all online/hybrid) | 0 Krakow; ~5 online/hybrid upcoming | 0 | 4 | Maybe (online AI hackathons only) |
| 9 | **Unstop** | `GET https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&per_page=50&oppstatus=open` | `search` param ignored; client-side only | 0 (268 open, all India-centric) | 0 | 2 | No |
| 10 | **DoraHacks** | None found (Nuxt SPA; `/api/hackathon/...` guesses all 404) | n/a | untested | untested | ? | No (unless someone sniffs XHR in a browser) |
| 11 | **Hackalist / hackathons.io** | Hackalist: static page, "archive 2014-2025"; hackathons.io redirects to `/lander` | n/a | 0 | 0 | dead | No |
| 12 | **Kaggle** | `/api/v1/competitions/list` -> 401; listing page -> reCAPTCHA challenge | n/a | n/a | n/a | 5 | No |
| 13 | **Challengepost** | = Devpost (same company/API) | | | | | covered by #1 |
| 14 | **Facebook Events** | No public API; HTML needs login | | | | | No (see sec. 14) |
| 15 | **ICS / Google Calendar** | Meetup per-group `.../events/ical/`, Luma `api.lu.ma/ics/get?entity=calendar&id=cal-...` | per group/calendar | n/a | n/a | 2 | Yes, as a per-organiser channel |

---

## 2. Devpost (and Challengepost)

* **API:** `https://devpost.com/api/hackathons` - unofficial but long-lived, JSON, no auth, no key. HTTP 200 from plain `requests`/curl.
* **Params that work:** `search`, `page`, `per_page` (up to 50 honoured), `status[]=upcoming|open|ended`, `challenge_type[]=online|in-person`, `open_to[]=public`, `order_by=recently-added`, `themes[]`, `length[]`, `amount[]`.
* **Params that do NOT work:** `location=Poland` -> still returns all 181 (ignored). There is no city/country filter.
* **Krakow filter = text search.** `search` matches title + displayed venue string (not city). Results:
  * `search=krakow` -> 6, `search=kraków` -> 10, `search=Cracow` -> 27 (fuzzy:true, noisy), `search=Poland` -> 29, `search=AGH` -> 11, `search=Hacknarok` -> 5.
  * **Gotcha:** `displayed_location.location` is often just a venue ("Lubicz", "Zabłocie 20", "Krakowski Park Technologiczny"), so the word "Krakow" is absent. Must also search organiser/venue keywords: `Hacknarok`, `AGH`, `Zabłocie`, `Krakowski`, `Cracow`, `Małopolskie`. A robust approach: run several searches, union by `id`, then fetch the hackathon page to confirm.
  * Sending non-ASCII through PowerShell pipes mangles it (`kraków` -> `krak?w`). Use Python source files with `\u00f3` or a UTF-8 script file.
* **Krakow hackathons found (all time, 11):** Hacknarök 2018, 2019, 2021 (online), VI 2022, VII 2023, VIII 2024, IX Apr 2025, **Hacknarok 18-19 Apr 2026**, **BLOCKCHAIN HACK KRAKOW 28-29 Mar 2026**, AGHacks 2014 & 2015. **Upcoming: none.** Hacknarok is annual (Mar/Apr, AGH) so expect a 2027 edition to appear around Jan-Mar 2027.
* **Also useful:** 58 online hackathons currently open/upcoming and open to the public (`challenge_type[]=online&open_to[]=public&status[]=upcoming&status[]=open`) - saved in `devpost_online_public_open.json`. Examples: *Build, Ship, Shape: Amazon Developer Hackathon* (31 Aug - 23 Oct 2026), *Nebius x NVIDIA Global AI Hackathon* (26 Aug - 30 Oct 2026), *OpenCV AI Competition 2026* (26 Aug - 27 Oct 2026). Need per-hackathon eligibility check (country exclusions) - not in the list API.
* **Sample (trimmed):**
  `{"id":29326,"title":"BLOCKCHAIN HACK KRAKOW","displayed_location":{"icon":"map-marker-alt","location":"Zabłocie 20 "},"open_state":"ended","url":"https://blockchain-hack-krakow.devpost.com/","submission_period_dates":"Mar 28 - 29, 2026","themes":[{"id":1,"name":"Blockchain"}],"prize_amount":"$<span data-currency-value>9,000</span>","registrations_count":3,"organization_name":"superteam", ...}`
  Dates are a display string (`"Apr 18 - 19, 2026"`), not ISO - must parse. Empty result shape: `{"hackathons":[],"meta":{"total_count":0,"per_page":9,"fuzzy":false}}`.
* **robots.txt:** `User-agent: * / Disallow:` (allow all), blocks a handful of AI/SEO bots (BLEXBot, Omgili, ImagesiftBot, Bytespider). API is not in robots. **ToS:** not reviewed line-by-line; Devpost's terms generally restrict automated scraping beyond personal use - treat as grey: low volume, cache, link back, attribute. Also `sitemap.xml` returned 404.
* **Fragility 2/5.** The endpoint has been stable for years and powers their own listing page. Risk: Cloudflare/rate-limit if hammered; undocumented.
* **Challengepost:** same company; `challengepost.com` is the legacy brand and shares the same data - nothing separate to integrate.

## 3. Luma (lu.ma / luma.com)

* `lu.ma` 301-redirects to `luma.com`; API host `api.lu.ma` (and `api2.luma.com`) both respond.
* **City pages:** `lu.ma/krakow` does **not** exist as a discover place (301 -> `/discover`). `GET https://api.lu.ma/discover/bootstrap-page?slug=krakow` returns the list of *launched* places - **no Krakow**; nearest are Warsaw (`discplace-PTcuEQVHuySJe8N`, 15 events, 252 km), Budapest, Vienna, Prague. `get-place-v2?slug=krakow` -> 404.
* **What works instead:**
  * `GET https://api.lu.ma/discover/get-paginated-events?latitude=50.0647&longitude=19.945&pagination_limit=50` -> 8 events near Krakow (all non-hackathon: yoga, AI x Voices, KRUG #4, Agentics meetup, Top Founder Summit Krakow...). Fields: `entries[].event.{api_id,name,start_at,end_at,url,location_type,geo_address_info{city,city_state,full_address},calendar_api_id,cover_url}`, plus `entries[].calendar`, `hosts`, `guest_count`, `ticket_info`. Pagination: `has_more`, `next_cursor` -> `pagination_cursor=`.
  * `radius` param appeared to be ignored (same 8 results with/without).
  * **Gotcha:** `query=` **together with lat/lon returns global results** (lat/lon ignored); `query=` alone does fuzzy text match and returns Krakow events when the query contains "krakow" (50 results, many irrelevant). So: use `query="hackathon krakow"` / `"hackathon poland"` / `"hackathon online"` and filter client-side on `geo_address_info` + title regex.
  * `https://api.lu.ma/search/get-results` -> **401 "You are not signed in."** (not usable).
* **Hackathons found:** Over 8 query variants (158 unique events), **zero hackathon-titled events in Poland**. Hackathons in the global results were in SF/NYC/Paris/London/Bengaluru/Madrid. Luma's discover only returns future events, so past-12-month count is unknown (no archive endpoint without auth).
* **Event page:** `https://lu.ma/<slug>` has `__NEXT_DATA__` with full event JSON (`props.pageProps.initialData`), no JSON-LD in my sample (1 ld+json block present).
* **ICS:** `https://api.lu.ma/ics/get?entity=calendar&id=cal-XXXX` returns a valid `text/calendar` feed (REFRESH-INTERVAL PT12H) with no auth - great for following specific Krakow organisers' calendars (e.g. the calendar_api_id seen on any event).
* **robots.txt:** only disallows `/social-share`, `/in/`, `/company/`, `/session-*` for Googlebot; points to `sitemap.luma.com/sitemap.xml`. API is not covered. ToS not reviewed; the discover API is the same the site uses (unofficial). There's an official Luma API but it needs a paid plan + API key and is for managing your own calendars.
* **Fragility 3/5** (unofficial, host has already moved lu.ma -> luma.com / api2; params like `radius` and `query` combos behave surprisingly).
* **Sample:** `{"entries":[{"api_id":"evt-...","event":{"name":"AI × Voices #1","start_at":"2026-10-06T...","url":"nu5jvdsm","geo_address_info":{"city_state":"Kraków, Poland"},"location_type":"offline"}}],"has_more":false}`

## 4. Meetup

* **Public page:** `https://www.meetup.com/find/?keywords=hackathon&location=pl--Krak%C3%B3w&source=EVENTS` -> 200, `__NEXT_DATA__` with `__APOLLO_STATE__` (18 events). **But the `keywords` filter is not applied in SSR** (results are generic Krakow events: Cloud and Data Meetup, DevFest Krakow...). Only ~20 events per page; no JSON-LD to speak of.
* **GraphQL:** `POST https://www.meetup.com/gql2` works **unauthenticated**, introspection is **open**. `Query.eventSearch(filter: EventSearchFilter!, first, after, sort)`. Filter fields: `lat`, `lon` (required), `radius`, `query`, `eventType` (PHYSICAL/ONLINE), `startDateRange`, `endDateRange`, `city`, `country`, `categoryId`, `topicCategoryId`, `zip`... Returns `totalCount`, `pageInfo{hasNextPage,endCursor}`, `edges[].node{id,title,dateTime,endTime,eventUrl,eventType,description,venue{name,city,country,address},group{name,urlname}}`.
  * Working query (verified): `query($f: EventSearchFilter!){ eventSearch(filter:$f, first:50){ totalCount edges{ node{ id title dateTime eventUrl eventType venue{city country} group{urlname} } } } }` with `{"f":{"lat":50.0647,"lon":19.945,"radius":100,"query":"hackathon"}}`.
  * `query` is **semantic/fuzzy** (embedding-like): "hackathon" returned cloud/devops meetups. Must regex-filter title + description yourself.
  * Scanned 8 queries (hackathon, hackaton, hakaton, hack, game jam, datathon, hackathon AI, buildathon) x up to 250 results, radius 100 km: 83 unique events, **0 real hackathons**. Closest: *Nighthack* at Hackerspace Krakow (9 Oct 2026, 20:00, hardware hacking night - not a hackathon in the competition sense) and *DevFest Krakow 2026* (10 Oct, GDG conference).
  * The old `/gql` endpoint returns 404; `gql2` is current. Official API (`api.meetup.com` / OAuth, Pro subscription for GraphQL) requires auth.
* **ICS/RSS:** `https://www.meetup.com/<group-urlname>/events/ical/` returns a valid `text/calendar` (tested on `hackerspacekrakow`) and `/events/rss/` returns RSS - **but robots.txt Disallows `*/events/rss/*`, `*/events/atom/*`, `*/calendar/*atom|rss|xml*`**; `/events/ical/` is not listed. Prefer iCal per group.
* **ToS/legal:** Meetup's terms forbid scraping/automated access without written consent; `gql2` is their internal API. Highest legal/ethical risk of the list. Fine for a low-volume personal tool; don't redistribute raw data; prefer per-group ICS for groups you curate (e.g. Hackerspace Krakow, GDG Krakow).
* **Fragility 4/5** (undocumented schema, could be locked down/rate-limited/captcha at any time).

## 5. MLH (mlh.io -> mlh.com)

* `mlh.io/seasons/2026/events` 301 -> `www.mlh.com/seasons/2026/events`. `/eu` -> latest season (2027). `/seasons/2019`, `/2020` -> 404; 2021-2027 work.
* **Data:** the page embeds Inertia JSON: `<script data-page="app" type="application/json">{...}</script>` -> `props.upcomingEvents[]` and `props.pastEvents[]`. (Not `__NEXT_DATA__`, no JSON-LD, no public JSON API; `/graphql` is in robots Disallow.)
* **Fields:** `id, slug, name, status, startsAt, endsAt, dateRange, url, location, formatType (physical|digital|hybrid_physical), region (AMER|EMEA|APAC|null), venueAddress{city,state,country}, websiteUrl, logoUrl, customFields`.
* **Krakow/Poland:** across seasons 2021-2027 (~1,500 events) **zero** events with `venueAddress.country == "PL"`. EMEA countries seen: GB 42, ES 6, SI 5, DE 5, RO 5, SK 4, DK 1, FI 1. Upcoming EMEA (Oct-Nov 2026): IKU Womxn in STEM (London, 17 Oct), OxHack '26 (Oxford, 24 Oct), UniHack (Timisoara, 13 Nov), DurHack (Durham, 14 Nov).
* **Useful bit:** `formatType=="digital"` events (Global Hack Week: Data/Agents, Midnight Virtual Hackathon) are online and open to Poland-based participants.
* **robots.txt:** Allow `/`; Disallow `/account/ /tools/ /graphql /v4/ ...`. Season pages are public. ToS not reviewed; MLH historically tolerated listing use; attribute and link back.
* **Fragility 2/5**; the markup moved from server HTML to Inertia JSON within the last couple of years (domain also changed), so expect another change eventually. Sample: `{"slug":"bigred-hacks-2026","name":"BigRed//Hacks 2026","startsAt":"2026-10-02T20:30:00Z","location":"Ithaca, New York","formatType":"physical","region":"AMER","venueAddress":{"city":"Ithaca","country":"US"}}`.

## 6. Devfolio

* **API:** `POST https://api.devfolio.co/api/search/hackathons` with JSON `{"type":"application_open","from":0,"size":100}` -> Elasticsearch-style `hits.hits[]._source`. Valid `type` values found: `application_open` (21 now) and `past` (1,734). `upcoming` -> 200 but empty; `all/open/live/ongoing/closed/featured` -> 422. Also the listing page has `__NEXT_DATA__` (react-query dehydrated state).
* **Fields:** `uuid, name, slug, starts_at, ends_at, is_online, city, country, location, timezone, themes, prizes, participants_count, desc (markdown), tagline, sponsor_tiers...`
* **Krakow/Poland:** no server-side location filter found; client-side `country=="Poland"`: only 2 in the entire history - *ETHWarsaw Hackathon 2024* (6 Sep 2024) and **ZK Hack Krakow (17 May 2024)**. 0 now, 0 in past 12 months. 15/21 current open ones are India; 735 of 1,755 have `country: null`, so null-country must be checked on `is_online`.
* **robots:** `User-agent: * / Disallow:` (allow all). ToS not reviewed. Fragility 2/5.

## 7. DoraHacks

* `https://dorahacks.io/hackathon` is a Nuxt SPA; HTML contains only banners; list is loaded client-side. Guessed endpoints (`/api/hackathon/`, `/api/hackathons`, `/api/buidl/hackathon/`, `/api/v2/hackathon/`, `api.dorahacks.io`) all 404 / DNS fail. Static JS chunks scanned for API paths - none found. `sitemap.xml` exists (200) but is tiny (3 KB). `robots.txt` -> 404.
* **I could not find a working endpoint.** The browser tool was unavailable in this session, so I could not sniff XHR. To finish: open DevTools Network on `/hackathon` and look for the XHR (likely under `/api/...` or a separate API host). Mostly Web3/crypto, global/online - low relevance to Krakow. **Result: failed / not recommended for v1.**

## 8. Eventbrite

* **Official API:** `GET https://www.eventbriteapi.com/v3/events/search/` -> **404 "path does not exist"** (event search was removed in 2020). Only per-organizer/venue/own-event endpoints remain, and they need an OAuth token.
* **Public page:** `https://www.eventbrite.com/d/poland--krak%C3%B3w/hackathon/` -> 200 (~580 KB). Contains 2 `application/ld+json` blocks (one is `ItemList` of `Event` with `name,startDate,url,location{name,address.addressLocality}`) **and** `window.__SERVER_DATA__` with `search_data.events.{results,pagination}` (`object_count`, `page_count`, `page_size`, `continuation`). Both parse fine.
* **But the keyword is not enforced:** `/hackathon/` and `/all-events/` return basically the same generic Krakow events (34 results for "hackathon": patisserie demo, escape game, SMA energy seminars, GoCracow #19...). **0 hackathons**, in either listing or `/d/online/hackathon/`. Eventbrite falls back to location-only when no keyword match.
* **robots.txt:** disallows `/rss/`, `/atom/`, `/events/rss/`, `/directory/`, `*?calendar*`, `*&id*`, `/api/v3/promoted/events`, `/api/v3/destination/search/log_requests/` etc. The internal `POST /api/v3/destination/search/` (405 on GET) is what the SPA uses; needs CSRF cookie - not tested further (out of bounds of "legit" use). Event pages themselves are fine.
* **Fragility 4/5**, anti-bot heavy; value ~0. **No.**

## 9. hackathon.com

* Server-rendered Marko app. `https://www.hackathon.com/city/poland/krakow` -> banner "There is no upcoming hackathons found in Krakow, Poland". Same for `/country/poland` and `/city/poland/warsaw`. `/online` lists 3 online events.
* `/city/poland/krakow/past` -> 16 historical results, paged at `/past/2`. Newest are 2022 meetups (e.g. *Femmegineering meetup* 22 Sep 2022, *Cracow Deep Learning Labs #1*); hackathons: AngelHack Krakow 2018, RealityHack @ TAURON Arena 2016, BeaconValley 2015/2016, #Map_IT! Mapping Hackathon. Country past: 47 events, e.g. *mObywatel mHack* (Wrocław). Many are Eventbrite imports (image URLs on `evbuc.com`).
* Event page `/event/<slug>-<id>` has JSON-LD `Event` (startDate, endDate, location, eventAttendanceMode). No API, no sitemap (`/sitemap.xml` 404). robots.txt allow-all. Year pages `/city/Poland/Krakow/2026` render 0 cards.
* **Fragility 3/5, value ~0 for current data.** No.

## 10. Hackathons.io, Hackalist, GitHub lists

* `hackathons.io` -> HTML with JS redirect to `/lander` (domain parked/dead).
* `hackalist.org`: AngularJS static site, meta says "An archive of hackathons from around the world (2014-2025)"; the old JSON API `/api/1.0/YYYY/MM.json` -> 404 for all months tested (2024-2026). GitHub repo `hackalist/hackalist.github.io` last commit 2026-04-09 but it is explicitly an archive. **Dead for current data.**
* GitHub search `hackathon list poland` found nothing relevant (only `awala/Awesome-Polish-AI`). No maintained machine-readable GitHub list for Poland was found in this pass; I did not do an exhaustive awesome-list crawl.

## 11. Lablab.ai

* `https://lablab.ai/ai-hackathons` (the `/event` URL redirects here), Next.js App Router, **no `__NEXT_DATA__`**; event objects are in the escaped RSC payload (`\"slug\":...,\"startAt\":...,\"endAt\":...,\"eventType\":\"ONLINE|HYBRID|ONSITE\",\"type\":\"HACKATHON\"`). Parsed 156 event objects (143 ONLINE, 12 HYBRID, 1 ONSITE) - see `lablab_events_parsed.json`. Only ~5 have `endAt` after today; the `status` field in the payload says `DRAFT` for everything (don't trust it). Upcoming examples: *AMD Developer Hackathon: ACT III* (12-18 Oct 2026, hybrid), *TechEx Amsterdam Hackathon* (16-19 Oct, hybrid), *Vultr: Agent Rush Hackathon* (3-8 Nov, hybrid), *Lablab x AMD AI Academy Challenge* (1 Sep - 1 Dec, online).
* No location data/field for Krakow. No JSON API found. `sitemap.xml` is an index of `server-sitemap/*` files. robots.txt disallows dashboards/auth only.
* **Fragility 4/5** (parsing React flight data). Only useful for online AI hackathons. Optional.

## 12. Unstop

* **API:** `GET https://unstop.com/api/public/opportunity/search-result?opportunity=hackathons&per_page=50&oppstatus=open&page=1` -> clean JSON (`data.data[]`: `id,title,start/end_date,region(offline|online|hybrid),locations[].{city,country},organisation,prizes,regnRequirements,seo_url,filters`), 268 open hackathons. robots.txt explicitly `Allow: /api/public/*`, `/hackathons/`.
* **Krakow/Poland:** `search=krakow` and `search=poland` both returned 6,622 (the param is ignored). Client-side scan of all 247 retrieved open items: **0** mention Poland/Krakow; locations are India. 99 are "online" but eligibility is typically Indian students/professionals (`regnRequirements`).
* Fragility 2/5; **value for Krakow: none.** No.

## 13. Kaggle & others

* Kaggle: `https://www.kaggle.com/api/v1/competitions/list` -> 401 "Unauthenticated"; competitions page served a reCAPTCHA challenge to curl. Kaggle has no "hackathon" location semantics anyway. Needs API token (free) if you ever want its competitions; skip for v1.
* Other global lists not tested live (no time / low odds): HackerEarth, TechGig, Hack Club, ETHGlobal (online/in-person global; has its own events page, worth a later look), Major hackathon chains (ETHWarsaw/Superteam Poland, Junction, HackZurich, etc. have own sites).

## 14. Facebook Events

* No public API for events (Graph API Events endpoints removed for public search in 2018; needs app review + user token for pages you manage). Public event pages require login / are heavily bot-blocked; scraping violates their ToS and risks IP/account bans. **Not feasible in a legit, low-maintenance way.** Alternatives: follow organiser sites/newsletters; use Meetup/Luma ICS where organisers cross-post; or manually curate Facebook-only events.

## 15. Google Calendar / ICS feeds

* Google Calendar has no discovery - you need a calendar ID. A public Google Calendar exposes `https://calendar.google.com/calendar/ical/<id>/public/basic.ics`, but only after you find the organiser's ID (e.g., on a hackathon organiser's site). Treat as per-organiser add-on.
* Working ICS tested: Meetup `/<group>/events/ical/` (200, `text/calendar`), Luma `api.lu.ma/ics/get?entity=calendar&id=cal-...` (200, 12 h refresh). Eventbrite has no ICS listing (only per-event "Add to calendar").
* **Recommended pattern:** maintain a curated list of ~10-30 Krakow organiser feeds (Hackerspace Krakow, GDG Krakow, AGH student clubs, KN Hacknarok, JUG/Python Krakow, etc.) and ingest ICS - robust, legit, low-maintenance, and the only way to catch Krakow events that never touch Devpost.

---

## 16. Actual upcoming events found

**No Krakow-based hackathon is listed on any tested global platform as of 3 Oct 2026.** Nearby / adjacent items worth surfacing manually (not hackathons per se):

| Event | Date | Where | URL |
|---|---|---|---|
| Nighthack - cut, solder & code (Hackerspace Kraków) | 9 Oct 2026, 20:00 | Kraków (ul. Limanowskiego 46) | https://www.meetup.com/hackerspacekrakow/events/316626986/ |
| DevFest Kraków 2026 (GDG conference, not hackathon) | 10 Oct 2026 | Zabłocie 20.22, Kraków | https://www.meetup.com/gdg-krakow/events/316006151/ |
| AGH Cyber Kampus 4.0 (check if competition format) | 26 Nov 2026 | Kraków | https://lu.ma/0sseer9f |
| Online, open-to-public (Devpost): Amazon Developer Hackathon | to 23 Oct 2026 | Online | https://amazonappdev2026.devpost.com/ |
| Online (Devpost): Nebius x NVIDIA Global AI Hackathon | to 30 Oct 2026 | Online | https://nebiusglobalaihackathon.devpost.com/ |
| Online (Devpost): OpenCV AI Competition 2026 | to 27 Oct 2026 | Online | https://opencv26.devpost.com/ |
| MLH Global Hack Week / digital events | rolling | Online | https://www.mlh.com/seasons/2027/events |

Past 12 months in Krakow (from Devpost): BLOCKCHAIN HACK KRAKOW (28-29 Mar 2026, Zabłocie 20, https://blockchain-hack-krakow.devpost.com/), Hacknarok (18-19 Apr 2026, https://hacknarok-180426.devpost.com/). Past 2024: ZK Hack Krakow (17 May 2024, Devfolio).

## 17. Recommendation for v1

1. **Devpost** - query set `{krakow, kraków, cracow, Hacknarok, AGH, Zabłocie, Małopolskie, Poland}` + the "online + public" list; union by `id`; classify by venue text; poll every 12-24 h.
2. **Luma** - lat/lon query + `query=hackathon krakow|poland|online` with client-side filter; plus ICS for specific organiser calendars.
3. **Curated ICS feeds** (Meetup per-group `ical`, Luma calendars, Google Calendar) for Krakow organisers.
4. **MLH** `digital` events only (optional).
5. **Meetup gql2** - optional/experimental, behind a feature flag (ToS risk, 4/5 fragility).
6. Skip hackathon.com, Eventbrite, Unstop, Hackalist, Kaggle, Facebook, DoraHacks (until XHR endpoint sniffed).

Add health checks: each fetcher should alert when it returns 0 results for >N runs, or when schema keys disappear. Given the low base rate of Krakow events on global platforms (about 2/year here), the Polish/local sources are the real value; global ones mainly provide the "online/hybrid, open to Poland" slice.

## 18. Caveats / honesty

* ToS were not read in full legal detail; the notes are based on robots.txt (fetched live) and general knowledge. Do your own check before commercial use.
* "Past 12 months" for Luma, Meetup, DoraHacks, Eventbrite is unknown/not verifiable via public endpoints (they show future events only or were untestable).
* DoraHacks endpoint discovery failed; browser tool was unavailable to sniff XHR.
* Devpost counts rely on text search, so venue-only listings could be missed.
* Files: `research/samples/probe_all.py` (runs all working probes), `devpost_*.json`, `luma_*.json`, `meetup_*.json`, `mlh_all_seasons.json`, `devfolio_*.json`, `eventbrite_krakow_hackathon_serverdata.json`, `unstop_hackathons_p1.json`, `lablab_events_parsed.json`.
