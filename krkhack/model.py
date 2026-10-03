from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field


@dataclass
class Cand:
    """Raw candidate emitted by a source adapter. Adapters only fill what they know."""
    title: str
    url: str
    source: str
    start: dt.datetime | dt.date | None = None
    end: dt.datetime | dt.date | None = None
    location: str = ""          # free text: venue / city
    country: str | None = None  # ISO-2 if the source knows it
    online: bool | None = None
    summary: str = ""
    kind_hint: str | None = None   # 'hackathon' | 'gamejam' | 'ctf' when the source is authoritative
    status: str = "confirmed"      # 'confirmed' | 'expected'
    extra: dict = field(default_factory=dict)
