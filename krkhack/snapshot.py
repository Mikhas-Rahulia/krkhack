"""Crossweb snapshot.

Crossweb (the best Polish source) sits behind a Cloudflare challenge that blocks every datacenter IP,
including GitHub Actions (verified: plain, TLS-impersonated and real headless Chrome all get 403).
A residential IP is let through, so a tiny job on a normal PC refreshes this snapshot and pushes it:

    python -m krkhack.snapshot          (see scripts/local_refresh.ps1 + scripts/install_task.ps1)

The cloud build uses live Crossweb when it can and falls back to the snapshot when it can't."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .model import Cand
from .util import as_date, iso, parse_iso, today

FILE = Path(__file__).resolve().parents[1] / "data" / "crossweb_snapshot.json"


def _dump(c: Cand) -> dict:
    return {"title": c.title, "url": c.url, "start": iso(c.start), "end": iso(c.end), "location": c.location,
            "country": c.country, "online": c.online, "kind_hint": c.kind_hint, "summary": c.summary}


def write(cands: list[Cand]) -> int:
    keep = [c for c in cands if c.start and as_date(c.end or c.start) >= today() - dt.timedelta(days=1)]
    FILE.parent.mkdir(exist_ok=True)
    FILE.write_text(json.dumps({"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                                "items": [_dump(c) for c in keep]}, ensure_ascii=False, indent=0), encoding="utf-8")
    return len(keep)


def read() -> tuple[list[Cand], float] | None:
    """-> (candidates, age_in_days) or None when no snapshot exists."""
    try:
        d = json.loads(FILE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None
    age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(d["generated"])).total_seconds() / 86400
    out = [Cand(title=i["title"], url=i["url"], source="crossweb", start=parse_iso(i["start"]), end=parse_iso(i.get("end")),
                location=i.get("location") or "", country=i.get("country"), online=i.get("online"),
                kind_hint=i.get("kind_hint"), summary=i.get("summary") or "") for i in d["items"]]
    return out, age


def main() -> int:
    import sys
    from .sources import crossweb
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    warns: list[str] = []
    try:
        cands, html_ok = crossweb.fetch_live({}, warns.append)
    except Exception as ex:  # noqa: BLE001
        print("Crossweb unreachable:", ex)
        return 1
    for w in warns:
        print("warn:", w)
    if not cands or not html_ok:
        print("Crossweb HTML not reachable/parsable - keeping previous snapshot")
        return 1
    print(f"snapshot written: {write(cands)} upcoming items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
