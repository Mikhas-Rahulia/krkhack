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

## Setup (once, ~3 minutes)
1. Push this folder to a **public** GitHub repo (public = unlimited free Actions minutes + Pages).
2. Repo → *Settings → Pages → Source: GitHub Actions*.
3. *Actions → update → Run workflow*. Done; it then runs daily at 05:17 UTC.

Optional secrets (Settings → Secrets and variables → Actions) — all improve recall, none are required:
`TAVILY_API_KEY` (1000 free searches/mo), `LLM_API_KEY` + `LLM_BASE_URL` + variable `LLM_MODEL` (e.g. a free Gemini key),
`TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`. Without `LLM_API_KEY` the workflow tries GitHub's free Models endpoint with the built-in token.

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
