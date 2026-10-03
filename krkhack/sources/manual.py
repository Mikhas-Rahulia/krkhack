"""Hand-curated events in data/manual.yml - the escape hatch for Facebook/Discord-only events
(just add 5 lines whenever you spot one; everything else is automatic)."""
from __future__ import annotations

from pathlib import Path

import yaml

from ..model import Cand
from ..util import parse_iso

FILE = Path(__file__).resolve().parents[2] / "data" / "manual.yml"


def fetch(cfg: dict, warn) -> list[Cand]:
    if not FILE.exists():
        return []
    out = []
    for e in yaml.safe_load(FILE.read_text(encoding="utf-8")) or []:
        start = parse_iso(str(e["start"])) if e.get("start") else None
        if not start:
            warn(f"manual entry without valid start: {e.get('title')}")
            continue
        out.append(Cand(title=e["title"], url=e["url"], source="manual", start=start,
                        end=parse_iso(str(e["end"])) if e.get("end") else None, location=e.get("location", ""),
                        country=e.get("country", "PL"), online=e.get("online"), summary=e.get("summary", ""),
                        kind_hint=e.get("kind", "hackathon")))
    return out
