# krkhack — Kraków hackathon aggregator that maintains itself

A GitHub Actions job runs daily, pulls hackathons / game jams / CTFs from ~10 sources, dedupes them, and publishes:

| Output | What for |
|---|---|
| `index.html` (GitHub Pages) | browse; grouped *In Kraków → Near Kraków → Poland → Expected → Online* |
| `krakow-hackathons.ics` | **subscribe once** in Google/Apple/Outlook calendar; events appear on their own |
| `feed.xml` | RSS of newly discovered events |
| `events.json`, `health.json` | machine-readable; per-source health |
| Telegram digest (optional) | push message when something new is found |

## Why it is built this way
Krakow has only ~25–35 public hackathons a year, and global platforms (Devpost, Luma, MLH…) list almost none of them.
So the feed is layered, and each layer covers for the others:

1. **Structured sources** (Crossweb, Devpost, Luma, MLH, Devfolio, CTFtime, GDG, Meetup iCal, JSON-LD pages).
2. **Series watchlist** (`data/series.yml`): ~22 annual events (HackYeah, BITEhack, Hacknarök, Kościuszkon, Global Game Jam…).
   Shown as *Expected* with a month window until real dates appear anywhere, then upgraded automatically. Their own sites are scanned for schema.org dates.
3. **Web-search discovery**: ~9 queries + a targeted query for every series about to happen → fetch → JSON-LD, else LLM extraction
   that must quote the date sentence verbatim from the page (otherwise dropped).
4. **Manual file** (`data/manual.yml`) for Facebook/Discord-only events: 5 lines per event.

## Self-healing
* Every source is isolated; one failing never breaks the build.
* Events that vanish from sources are kept for 14 days (flaky parsers, paging).
* Plain HTTP blocked by Cloudflare → transparently retried with Chrome TLS impersonation (`curl_cffi`) — works from a home IP.
* Crossweb: live HTML → live RSS → last snapshot; if the HTML parser matches 0 rows it raises a flag (markup changed).
* `data/health.json` tracks each source's item-count history; a source returning 0 / <25% of its median for 3 runs
  turns `degraded`, and the workflow opens (and later auto-closes) a GitHub issue **"Hackathon sources need attention"**.
* Committing `data/` every run stops GitHub from disabling the schedule after 60 inactive days.

## What runs where (verified, not assumed)
GitHub's datacenter IPs are blocked by several things we'd like to use, so:

| Piece | Runs in the cloud? | Notes |
|---|---|---|
| Devpost, Luma, MLH, Devfolio, CTFtime, GDG, Meetup iCal, JSON-LD pages, series, manual | ✅ fully automatic | zero upkeep |
| **Crossweb** (biggest Polish source) | ⚠️ blocked by Cloudflare from GitHub (403 even with a real headless Chrome) | a tiny job on **your PC** refreshes `data/crossweb_snapshot.json` daily (`scripts/install_task.ps1`). If it stops, the build raises an issue after 8 days. |
| **Web-search discovery** | ⚠️ DuckDuckGo/Brave/Mojeek block datacenter IPs | needs the free **`TAVILY_API_KEY`** secret (1000 searches/mo, no card). Without it the build flags it in the health table / issue. |
| LLM date extraction | best effort | uses `LLM_API_KEY` if set, else tries GitHub's free Models endpoint with the built-in token (untested; failure is non-fatal) |

## Setup
1. Repo is public (unlimited free Actions + Pages). *Settings → Pages → Source: GitHub Actions*.
2. *Actions → update → Run workflow* (then it runs daily at 05:17 UTC).
3. **Recommended:** add secret `TAVILY_API_KEY` (tavily.com, free) and run `scripts\install_task.ps1` once on your PC.
4. Optional: `LLM_API_KEY` (+ `LLM_BASE_URL`, variable `LLM_MODEL`; e.g. a free Gemini key), `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` for push digests.

## Everyday use
* Just open the page / subscribe to the `.ics`. Nothing to do.
* Spotted something only on Facebook? Add a block to `data/manual.yml`.
* New recurring event? Add a block to `data/series.yml`. New Meetup group? Add its iCal URL to `config.yml → sources.ics.feeds`.

## Local
```
pip install -r requirements.txt
python -m krkhack --out site --no-notify      # build
python -m pytest -q                           # tests
```
Research notes that led to these choices: `research/` (platforms, organizers, Polish sources).
