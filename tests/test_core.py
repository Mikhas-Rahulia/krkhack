import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from krkhack import discovery, pipeline, series as series_mod
from krkhack.classify import audience_of, kind_of, locate
from krkhack.model import Cand
from krkhack.sources import crossweb, ics
from krkhack.util import parse_devpost_range

REF = dt.date(2026, 10, 3)
SERIES = series_mod.load()
CFG = {"horizon_days": 400}


# ---------------------------------------------------------------- classification
def test_kind_of():
    assert kind_of("HackYeah 2026") == "hackathon"
    assert kind_of("Global Game Jam Kraków") == "gamejam"
    assert kind_of("AGH Cyber Kampus CTF") == "ctf"
    assert kind_of("Nighthack - wpadnij") == "hacknight"
    assert kind_of("Hackathon dla Małopolski") == "hackathon"
    assert kind_of("DevFest Kraków 2026") is None
    assert kind_of("Hackerspace open day") is None
    assert kind_of("Life hack: sleep better") is None
    assert kind_of("Kościuszkon IV", series_mod.patterns(SERIES)) == "hackathon"


def test_locate():
    assert locate("Zabłocie 20")[0] == "krakow"
    assert locate("AGH, Pawilon B-1")[0] == "krakow"
    assert locate("Katowice")[0] == "nearby"
    assert locate("Warszawa", country="PL")[0] == "poland"
    assert locate("Online", online=True)[0] == "online"
    assert locate("New York, NY, USA")[0] is None
    assert locate("Berlin")[0] is None


def test_audience():
    assert audience_of("Studencki Hackathon AI") == "students"
    assert audience_of("only vocational secondary-school students") == "pupils"
    assert audience_of("HackYeah 2026") == "open"


# ---------------------------------------------------------------- parsing
def test_devpost_range():
    assert parse_devpost_range("Mar 28 - 29, 2026") == (dt.date(2026, 3, 28), dt.date(2026, 3, 29))
    assert parse_devpost_range("Oct 06, 2026 - Jan 12, 2027") == (dt.date(2026, 10, 6), dt.date(2027, 1, 12))
    assert parse_devpost_range("Dec 28 - Jan 04, 2027") == (dt.date(2026, 12, 28), dt.date(2027, 1, 4))
    assert parse_devpost_range("garbage") is None


def test_ics_parse():
    txt = ("BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nSUMMARY:Nighthack\\, fun\r\nDTSTART;TZID=Europe/Warsaw:20261009T200000\r\n"
           "DTEND;TZID=Europe/Warsaw:20261009T230000\r\nURL:https://x.test/e\r\nLOCATION:Limanowskiego 46\r\nEND:VEVENT\r\n"
           "BEGIN:VEVENT\r\nSUMMARY:All day jam\r\nDTSTART;VALUE=DATE:20270125\r\nEND:VEVENT\r\nEND:VCALENDAR")
    ev = ics.parse_ics(txt, "t")
    assert len(ev) == 2 and ev[0].title == "Nighthack, fun" and ev[0].start.hour == 20
    assert ev[1].start == dt.date(2027, 1, 25)


CW_HTML = """<div class="event-list"><div class="monthsbox"><div class="calendar-date"><div>Październik</div>
<div class="monthbox-year"><span>&nbsp;</span>2026</div></div><div class="list">
<div class="tab-row"><a href="/wydarzenia/growup-hackathon-2026/"><div class="colTab date"><div class="first">
<div class="num">20.10</div></div></div><div class="colTab title">GrowUp Hackathon 2026<div class="topics">IT</div></div>
<div class="colTab city">Online</div><div class="colTab type">Hackathon</div></a></div>
<div class="tab-row"><a href="/wydarzenia/hy/"><div class="colTab date"><div class="first"><div class="num">03.10</div></div>
<div class="second"><div class="num">- 04.10</div></div></div><div class="colTab title">HackYeah 2026</div>
<div class="colTab city">Kraków</div><div class="colTab type">Hackathon</div></a></div></div></div></div>
<div class="event-list old"><div class="monthsbox"><div class="calendar-date"><div>Wrzesień</div><div class="monthbox-year">2026</div></div>
<div class="tab-row"><a href="/wydarzenia/old/"><div class="colTab date"><div class="num">01.09</div></div>
<div class="colTab title">Old Hackathon</div><div class="colTab city">Warszawa</div></a></div></div></div>"""


def test_crossweb_parse():
    c = crossweb.parse_html(CW_HTML)
    assert [x.title for x in c] == ["GrowUp Hackathon 2026", "HackYeah 2026"]
    assert c[1].start == dt.date(2026, 10, 3) and c[1].end == dt.date(2026, 10, 4) and c[1].location == "Kraków"
    assert c[0].online is True and c[0].kind_hint == "hackathon"


# ---------------------------------------------------------------- pipeline logic
def _norm(**kw):
    base = dict(title="X Hackathon", url="https://x.test/", source="crossweb",
                start=dt.date(2026, 11, 1), location="Kraków", country="PL")
    base.update(kw)
    return pipeline.normalize(Cand(**base), SERIES, CFG, REF)


def test_normalize_drops_irrelevant():
    assert _norm(title="DevFest Kraków 2026") is None           # not a hackathon
    assert _norm(location="New York, NY, USA", country=None) is None  # abroad
    assert _norm(start=None) is None
    assert _norm()["tier"] == "krakow"


def test_dedupe_across_sources():
    a = _norm(title="Blockchain Hack Kraków – październik 2026", url="https://crossweb.pl/wydarzenia/bh/", start=dt.date(2026, 10, 17))
    b = _norm(title="Blockchain Hack Kraków (autumn)", url="https://lu.ma/bh", source="luma", start=dt.date(2026, 10, 17), end=dt.date(2026, 10, 18))
    c = _norm(title="Totally Different Hackathon", url="https://other.test", start=dt.date(2026, 10, 17))
    out = pipeline.dedupe([a, b, c])
    assert len(out) == 2
    merged = next(e for e in out if "Blockchain" in e["title"])
    assert set(merged["sources"]) == {"crossweb", "luma"} and len(merged["links"]) == 2


def test_dedupe_does_not_merge_far_apart_editions():
    a = _norm(title="Foo Hackathon", url="https://a.test/1", start=dt.date(2026, 11, 1))
    b = _norm(title="Foo Hackathon", url="https://a.test/2", start=dt.date(2027, 5, 1))
    assert len(pipeline.dedupe([a, b])) == 2


def test_expected_series_and_confirmation():
    exp = series_mod.expected_events(SERIES, [], {}, REF)
    titles = " ".join(e["title"] for e in exp)
    assert "Hacknar" in titles and "Global Game Jam" in titles
    # once a confirmed edition exists, the placeholder disappears
    confirmed = [_norm(title="Hacknarök 2027", start=dt.date(2027, 4, 10))]
    exp2 = series_mod.expected_events(SERIES, confirmed, {}, REF)
    assert "Hacknar" not in " ".join(e["title"] for e in exp2)
    # an edition that just happened pushes the next window to next year
    exp3 = series_mod.expected_events(SERIES, [], {"hackyeah": "2026-10-04"}, REF)
    assert not any(e["series"] == "hackyeah" for e in exp3)


def test_collapse_recurring():
    evs = [_norm(title="Nighthack #%d" % i, url="https://m.test/%d" % i, start=dt.date(2026, 10, 9 + 7 * i), source="ics:x") for i in range(3)]
    out = pipeline.collapse_recurring(evs)
    assert len(out) == 1 and out[0]["more"] == 2


def test_health_flags_collapse():
    h = {"sources": {"crossweb": {"history": [170, 165, 172], "bad_streak": 2}}}
    res = {"crossweb": {"ok": True, "cands": [], "error": None, "warnings": [], "secs": 1}}
    out = pipeline.update_health(res, {}, {"health": {"degraded_after_runs": 3}}, h)
    assert out["sources"]["crossweb"]["status"] == "degraded"


# ---------------------------------------------------------------- discovery hallucination guard
def test_llm_events_require_verbatim_evidence(monkeypatch):
    page = "Welcome! The Kraków AI Hackathon takes place on 12 December 2026 at Zabłocie. Register now."
    good = '{"events":[{"title":"Kraków AI Hackathon","start":"2026-12-12","location":"Zabłocie","online":false,"evidence":"The Kraków AI Hackathon takes place on 12 December 2026"}]}'
    bad = '{"events":[{"title":"Made Up Jam","start":"2026-12-12","evidence":"Made Up Jam will be held on 12 December 2026 in Kraków"}]}'
    assert len(discovery.parse_llm_events("```json\n" + good + "\n```", page, "https://x.test")) == 1
    assert discovery.parse_llm_events(bad, page, "https://x.test") == []
    assert discovery.parse_llm_events("not json", page, "https://x.test") == []


# ---------------------------------------------------------------- crossweb snapshot fallback
def test_crossweb_falls_back_to_snapshot_and_flags_stale(monkeypatch, tmp_path):
    from krkhack import snapshot
    monkeypatch.setattr(snapshot, "FILE", tmp_path / "snap.json")
    snapshot.write([Cand(title="Snap Hackathon", url="https://crossweb.pl/wydarzenia/snap/", source="crossweb",
                         start=dt.date.today() + dt.timedelta(days=20), location="Kraków")])
    # Cloudflare blocks the cloud: live fetch yields nothing
    monkeypatch.setattr(crossweb, "fetch_live", lambda cfg, warn: ([], False))
    warns = []
    got = crossweb.fetch({}, warns.append)
    assert [c.title for c in got] == ["Snap Hackathon"]
    assert not any(w.startswith("!") for w in warns)          # fresh snapshot: fine
    # make the snapshot 12 days old -> the home job has stopped -> human-attention flag
    import json
    d = json.loads(snapshot.FILE.read_text(encoding="utf-8"))
    d["generated"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=12)).isoformat(timespec="seconds")
    snapshot.FILE.write_text(json.dumps(d), encoding="utf-8")
    warns.clear()
    crossweb.fetch({}, warns.append)
    assert any(w.startswith("!") and "snapshot" in w for w in warns)


def test_crossweb_without_snapshot_raises(monkeypatch, tmp_path):
    from krkhack import snapshot
    monkeypatch.setattr(snapshot, "FILE", tmp_path / "none.json")
    monkeypatch.setattr(crossweb, "fetch_live", lambda cfg, warn: ([], False))
    import pytest
    with pytest.raises(RuntimeError):
        crossweb.fetch({}, lambda w: None)


def test_flagged_warning_marks_source_unhealthy():
    res = {"discovery": {"ok": True, "cands": [], "error": None, "warnings": ["x", "! add TAVILY key"], "secs": 0}}
    out = pipeline.update_health(res, {}, {"health": {"degraded_after_runs": 1}}, {})
    assert out["sources"]["discovery"]["status"] == "degraded"
    assert out["sources"]["discovery"]["flag"] == "add TAVILY key"


def test_discovery_uses_search_api_text_when_page_blocked(monkeypatch, tmp_path):
    """Crossweb 403s us, but Tavily already crawled the page: LLM extraction must run on that text."""
    page = "GrowUp Hackathon 2026 odbędzie się 12 grudnia 2026 w Krakowie. Zapisy trwają."
    monkeypatch.setattr(discovery, "CACHE", tmp_path / "cache.json")
    monkeypatch.setattr(discovery, "search", lambda q, n, domains=None: [
        {"title": "GrowUp", "url": "https://crossweb.pl/wydarzenia/new-hack/", "snippet": "", "text": page}])
    monkeypatch.setattr(discovery, "extract", lambda url: (_ for _ in ()).throw(RuntimeError("403 Cloudflare")))
    monkeypatch.setenv("LLM_API_KEY", "x")
    monkeypatch.setattr(discovery, "_llm", lambda prompt: '{"events":[{"title":"New Hack Kraków","start":"2026-12-12","location":"Kraków","online":false,"evidence":"GrowUp Hackathon 2026 odbędzie się 12 grudnia 2026 w Krakowie"}]}')
    out = discovery.run({"queries": [], "domain_queries": [{"q": "hackathon Kraków", "domains": ["crossweb.pl"]}]}, lambda w: None, set())
    assert [c.title for c in out] == ["New Hack Kraków"]
