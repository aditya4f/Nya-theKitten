"""Mood- and context-aware one-liners for the thought box."""

from __future__ import annotations

import random
import re

BY_MOOD = {
    "idle": ["nya~", "mrrp...", ":3", "hehe~", "nya nya", "...", "hm."],
    "happy": ["nya nya!", "purrrr", "hehe~", ":3", "warm.", "best day"],
    "curious": ["what's that?", "hmm?", "I'm watching you...", "oh?", "wait."],
    "sleepy": ["mrrp...", "zzz", "five more min", "so sleepy", "blanket..."],
    "excited": ["nya!!", "again again", "pounce!", "can't sit still"],
    "annoyed": ["hmmph", "excuse me", "rude.", "not now", "...really"],
    "playing": ["catch me!", "nya!!", "pounce!", "again!", "hehe~"],
    "sleeping": ["zzz...", "mrrp...", "zzz zzz", "..."],
}

HUNGRY = ["feed me pls", "stomach...", "tuna...?", "is it dinner", "hungry nya"]
CLINGY = ["pet me pls", "hold me", "don't go", "more pets", "stay?"]
SASSY = ["I saw that", "try harder", "hmmph", "you're late", "notes taken"]

_CONTEXT = (
    (re.compile(r"\b(hi|hello|hey|yo)\b", re.I), ["hi hi", "nya~ hello", "you came back"]),
    (re.compile(r"\b(love|cute|pretty|good (?:boy|girl|cat)|best)\b", re.I), ["hehe~", "stop it :3", "purrrr"]),
    (re.compile(r"\b(food|treat|tuna|snack|fish|milk)\b", re.I), ["where??", "yes please", "tuna...!"]),
    (re.compile(r"\b(sleep|nap|bed|tired)\b", re.I), ["already yawning", "blanket yes", "zzz soon"]),
    (re.compile(r"\b(no|bad|stop|stupid|dumb)\b", re.I), ["rude.", "hmmph", "wow."]),
    (re.compile(r"\b(play|ball|chase|game)\b", re.I), ["YES", "pounce ready", "throw it"]),
    (re.compile(r"\b(bye|leave|gone|later)\b", re.I), ["don't go", "stay a bit", "...okay"]),
)


def _pick(lines, rng=random.random):
    if not lines:
        return "nya~"
    return lines[int(rng() * len(lines)) % len(lines)]


def thought_for_mood(state, rng=random.random):
    if state.get("hunger", 0) > 78:
        return _pick(HUNGRY, rng)
    if state.get("mood") == "idle" and state.get("traits", {}).get("clingy", 0) > 0.65 and rng() < 0.45:
        return _pick(CLINGY, rng)
    if state.get("mood") == "annoyed" or (
        state.get("traits", {}).get("sassy", 0) > 0.7 and rng() < 0.35
    ):
        return _pick(SASSY, rng)
    return _pick(BY_MOOD.get(state.get("mood"), BY_MOOD["idle"]), rng)


def thought_for_talk(state, text, rng=random.random):
    for pattern, lines in _CONTEXT:
        if pattern.search(text or ""):
            return _pick(lines, rng)
    if state.get("mood") == "sleeping":
        return _pick(["...zzz", "five more min", "mrrp..."], rng)
    if state.get("traits", {}).get("sassy", 0) > 0.6 and rng() < 0.4:
        return _pick(SASSY, rng)
    curious = dict(state)
    curious["mood"] = "curious"
    return thought_for_mood(curious, rng)


def meter_bar(value, width=10):
    n = max(0, min(100, float(value)))
    filled = int(round(n / (100.0 / width)))
    filled = max(0, min(width, filled))
    return ("#" * filled) + ("-" * (width - filled))


def status_lines(state, now_ms=None):
    import time

    if now_ms is None:
        now_ms = int(time.time() * 1000)
    age = max(0, now_ms - int(state.get("bornAt", now_ms)))
    hours, rem = divmod(age // 1000, 3600)
    mins = rem // 60
    name = state.get("name", "Mochi")
    mood = state.get("mood", "idle")
    return [
        "%s · %s" % (name, mood),
        "hunger    %s %d" % (meter_bar(state.get("hunger", 0)), int(round(state.get("hunger", 0)))),
        "happiness %s %d" % (meter_bar(state.get("happiness", 0)), int(round(state.get("happiness", 0)))),
        "energy    %s %d" % (meter_bar(state.get("energy", 0)), int(round(state.get("energy", 0)))),
        "pets %d  feeds %d  plays %d"
        % (state.get("pets", 0), state.get("feeds", 0), state.get("plays", 0)),
        "age %dh %dm" % (hours, mins),
    ]
