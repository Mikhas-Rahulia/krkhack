"""python -m krkhack [--out site] [--base-url URL] [--no-notify] [--no-discovery]"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import notify, pipeline, render


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="krkhack")
    ap.add_argument("--out", default="site")
    ap.add_argument("--base-url", default="")
    ap.add_argument("--no-notify", action="store_true")
    ap.add_argument("--no-discovery", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    cfg = pipeline.load_config()
    if a.no_discovery:
        cfg.setdefault("discovery", {})["enabled"] = False
    result = pipeline.run(cfg)
    render.build(result, Path(a.out), base_url=a.base_url)

    ev = result["events"]
    conf = [e for e in ev if e["status"] == "confirmed"]
    by_tier = {t: sum(e["tier"] == t for e in conf) for t in ("krakow", "nearby", "poland", "online")}
    print(f"events: {len(conf)} confirmed {by_tier}, {len(ev) - len(conf)} expected")
    bad = {n: h["status"] for n, h in result["health"]["sources"].items() if h["status"] != "ok"}
    for n, h in result["health"]["sources"].items():
        print(f"  {n:14s} {h['status']:9s} raw={h['raw']:<4} kept={h['kept']:<3} {h.get('error') or ''}")
    if bad:
        Path("data").mkdir(exist_ok=True)
    alerts = {n: s for n, s in bad.items() if s in ("degraded", "down")}
    Path("data/alerts.md").write_text(
        "" if not alerts else "Sources needing attention:\n" + "\n".join(
            f"- **{n}**: {s} - {result['health']['sources'][n].get('error') or 'returning far fewer items than usual'}"
            for n, s in alerts.items()) + "\n", encoding="utf-8")
    if not a.no_notify:
        fresh = notify.new_events(ev)
        if fresh:
            try:
                if notify.send_telegram(notify.digest(fresh)):
                    print(f"telegram: sent {len(fresh)} new")
            except Exception as ex:  # noqa: BLE001
                print("telegram failed:", ex)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
