"""Optional passive notifications. Set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID as repo secrets and a
digest of newly discovered on-site events is pushed to you; otherwise this is a silent no-op."""
from __future__ import annotations

import datetime as dt
import os

from .render import fmt_when
from .util import http


def new_events(events: list[dict], days: int = 1) -> list[dict]:
    cut = (dt.date.today() - dt.timedelta(days=days - 1)).isoformat()
    return [e for e in events if e["status"] == "confirmed" and e["tier"] in ("krakow", "nearby", "poland")
            and e.get("first_seen", "") >= cut and not e.get("stale")]


def digest(events: list[dict]) -> str:
    lines = ["\U0001F195 Nowe hackathony w Krakowie i okolicy:"]
    for e in events[:12]:
        lines.append(f"\u2022 {e['title']} \u2014 {fmt_when(e)} ({e.get('location') or e['tier']})\n  {e['url']}")
    return "\n".join(lines)


def send_telegram(text: str) -> bool:
    tok, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not (tok and chat):
        return False
    http(f"https://api.telegram.org/bot{tok}/sendMessage", method="POST",
         json={"chat_id": chat, "text": text, "disable_web_page_preview": True})
    return True
