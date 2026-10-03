"""Decide whether a candidate is a hackathon-type event and where it sits relative to Krakow."""
from __future__ import annotations

import re

# --- what counts as a hackathon-type event -------------------------------------------------
_HACK = re.compile(
    r"hack(?!er(?:s|space|news)\b)|hakat|hackaton|game\s?jam|\bgamejam\b|datath|code?athon|"
    r"buildathon|ideathon|\b(?:ai|ml|data|code|build|idea|dev|design)thon\b|\bctf\b|capture the flag|"
    r"\bglobal game jam\b|\bnighthack\b", re.I)
_NOT_HACK = re.compile(r"hackerspace open|hacker news|life ?hack|growth hack", re.I)


def kind_of(title: str, extra_patterns: list[re.Pattern] | None = None) -> str | None:
    t = title or ""
    if _NOT_HACK.search(t):
        return None
    if re.search(r"\bctf\b|capture the flag", t, re.I):
        return "ctf"
    if re.search(r"game\s?jam|gamejam", t, re.I):
        return "gamejam"
    if re.search(r"nighthack|hack ?night", t, re.I):
        return "hacknight"
    if _HACK.search(t):
        return "hackathon"
    for p in extra_patterns or []:
        if p.search(t):
            return "hackathon"
    return None


# --- geography ------------------------------------------------------------------------------
KRAKOW = re.compile(
    r"krak[o\u00f3]w|cracow|krakau|\bkrk\b|zab\u0142ocie|zablocie|nowa huta|tauron arena|expo krak|"
    r"\bagh\b|akademia g\u00f3rniczo|jagiello|politechnika krakowska|cyfronet|bonarka|podg\u00f3rze", re.I)
NEARBY = re.compile(
    r"ma\u0142opolsk|malopolsk|tarn[o\u00f3]w|nowy s[a\u0105]cz|zakopane|wieliczka|o\u015bwi\u0119cim|oswiecim|"
    r"bochnia|nowy targ|my\u015blenice|olkusz|chrzan[o\u00f3]w|skawina|niepo\u0142omice|katowice|gliwice|"
    r"bielsko|cz\u0119stochowa|czestochowa|rzesz[o\u00f3]w|kielce|opole|sosnowiec|zabrze|bytom|tychy", re.I)
POLAND = re.compile(
    r"poland|polska|polen|pologne|warszaw|warsaw|wroc\u0142aw|wroclaw|pozna\u0144|poznan|gda\u0144sk|gdansk|"
    r"gdynia|sopot|\u0142\u00f3d\u017a|lodz|szczecin|lublin|bia\u0142ystok|bialystok|toru\u0144|torun|bydgoszcz|"
    r"olsztyn|stalowa wola|radom|rzesz", re.I)
ONLINE = re.compile(r"\bonline\b|virtual|remote|worldwide|everywhere|zdaln", re.I)

TIERS = ("krakow", "nearby", "poland", "online")


def locate(text: str, *, country: str | None = None, online: bool | None = None) -> tuple[str | None, bool]:
    """Return (tier, is_online). tier None => not relevant (abroad)."""
    text = text or ""
    is_online = bool(online) or (online is None and bool(ONLINE.search(text)))
    if KRAKOW.search(text):
        return "krakow", is_online
    if NEARBY.search(text):
        return "nearby", is_online
    if (country or "").upper() == "PL" or POLAND.search(text):
        # a purely virtual event that merely mentions Poland is still an online event
        return ("online" if online else "poland"), is_online
    if is_online:
        return "online", True
    return None, False


def audience_of(text: str) -> str:
    t = (text or "").lower()
    if re.search(r"uczni|pupils|secondary[- ]school|szk\u00f3\u0142 ponadpodstaw|high[- ]school students|dla m\u0142odzie\u017cy|school students", t):
        return "pupils"
    if re.search(r"\bstudenck|\bstudents?\b|dla student|student hackathon|studencki", t):
        return "students"
    return "open"
