"""python -m krkhack.verify  — run EVERY source live, independently, and show hard evidence:
did the endpoint answer, how many raw records, how many survive filtering, date range, a sample.
Also round-trips the published ICS to prove the calendar feed parses."""
from __future__ import annotations

import sys
import time

from . import pipeline, series as series_mod
from .sources import REGISTRY
from .sources.ics import parse_ics
from .util import Reporter, as_date, today


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    cfg = pipeline.load_config()
    series_list = series_mod.load()
    bad = 0
    print(f"{'source':12s} {'result':8s} {'scanned':>7s} {'cands':>5s} {'relevant':>8s} {'future':>6s}  date-range / note")
    for name, scfg in cfg["sources"].items():
        if not scfg.get("enabled", True):
            print(f"{name:12s} disabled")
            continue
        rep = Reporter()
        t0 = time.time()
        try:
            cands = REGISTRY[name](scfg, rep)
            err = None
        except Exception as ex:  # noqa: BLE001
            cands, err = [], str(ex)[:90]
        rel = [e for e in (pipeline.normalize(c, series_list, cfg, today()) for c in cands) if e]
        fut = [c for c in cands if c.start and as_date(c.end or c.start) >= today()]
        scanned = rep.scanned or len(cands)
        ok = err is None and scanned > 0
        bad += not ok
        rng = ""
        if cands:
            ds = sorted(as_date(c.start) for c in cands if c.start)
            rng = f"{ds[0]} .. {ds[-1]}" if ds else ""
        note = err or (rep.warnings[0][:70] if rep.warnings else "")
        print(f"{name:12s} {'OK' if ok else 'FAIL':8s} {scanned:7d} {len(cands):5d} {len(rel):8d} {len(fut):6d}  {rng} {note}  [{time.time() - t0:.1f}s]")
    # ICS round trip
    ics_file = pipeline.ROOT / "site" / "krakow-hackathons.ics"
    if ics_file.exists():
        parsed = parse_ics(ics_file.read_text(encoding="utf-8"), "roundtrip")
        print(f"\nICS round-trip: {len(parsed)} events parsed from site/krakow-hackathons.ics")
    print(f"\n{'ALL SOURCES ALIVE' if not bad else str(bad) + ' source(s) FAILED'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
