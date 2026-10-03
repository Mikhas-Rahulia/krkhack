"""Source registry. Each adapter exposes fetch(cfg: dict, warn: callable) -> list[Cand].
Adding a source = one file + one line here + one block in config.yml."""
from . import crossweb, ctftime, devfolio, devpost, gdg, ics, luma, manual, mlh, pages

REGISTRY = {
    "crossweb": crossweb.fetch,
    "devpost": devpost.fetch,
    "luma": luma.fetch,
    "mlh": mlh.fetch,
    "devfolio": devfolio.fetch,
    "gdg": gdg.fetch,
    "ctftime": ctftime.fetch,
    "ics": ics.fetch,
    "pages": pages.fetch,
    "manual": manual.fetch,
}
