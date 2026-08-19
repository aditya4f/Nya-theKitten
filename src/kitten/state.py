"""Personality, stats, and the living-kitten state machine.

This module is deliberately free of terminal I/O so tests can drive it
without a TTY. Time is always passed in as milliseconds.
"""

from __future__ import annotations

import random
import time

from .sprites import CUTE_POOL
from .thoughts import thought_for_mood, thought_for_talk

MOODS = ("idle", "happy", "curious", "sleepy", "excited", "annoyed", "playing", "sleeping")
LOG_CAP = 8
THOUGHT_MS = 3200
POSE_SHORT = 700
POSE_MED = 1400
POSE_LONG = 2600

HELP_LINES = [
    "pet     scratch behind the ears",
    "feed    offer a snack",
    "play    toss something shiny",
    "sleep   dim the lights",
    "wake    rustle the blanket",
    "status  inspect the creature",
    "name    give a new name",
    "q       leave quietly",
]


def now_ms():
    return int(time.time() * 1000)


def clamp(n, lo=0.0, hi=100.0):
    return max(lo, min(hi, float(n)))


def _traits(rng=random.random):
    return {
        "clingy": round(0.25 + rng() * 0.7, 2),
        "sassy": round(0.15 + rng() * 0.7, 2),
        "sleepy": round(0.2 + rng() * 0.7, 2),
    }


def create_kitten(name="Mochi", now=None, rng=random.random):
    if now is None:
        now = now_ms()
    return {
        "name": name,
        "hunger": 28.0,
        "happiness": 72.0,
        "energy": 78.0,
        "mood": "curious",
        "pose": "sit",
        "poseUntil": now + 1200,
        "thought": "nya~",
        "thoughtUntil": now + 4000,
        "look": 0,
        "lastInteractAt": now,
        "lastTickAt": now,
        "bornAt": now,
        "pets": 0,
        "feeds": 0,
        "plays": 0,
        "traits": _traits(rng),
        "log": [{"at": now, "text": "%s arrived." % name}],
        "offsetX": 0.0,
        "input": "",
    }


def snapshot(state):
    return {
        "name": state["name"],
        "hunger": state["hunger"],
        "happiness": state["happiness"],
        "energy": state["energy"],
        "mood": state["mood"],
        "pets": state["pets"],
        "feeds": state["feeds"],
        "plays": state["plays"],
        "traits": dict(state["traits"]),
        "bornAt": state["bornAt"],
        "lastTickAt": state["lastTickAt"],
    }


def hydrate(snap, now=None):
    if now is None:
        now = now_ms()
    base = create_kitten(snap.get("name", "Mochi"), snap.get("bornAt", now))
    base.update(snap)
    base["pose"] = "sleep" if snap.get("mood") == "sleeping" else "sit"
    base["poseUntil"] = now + 800
    base["thought"] = "zzz..." if snap.get("mood") == "sleeping" else "you're back"
    base["thoughtUntil"] = now + 3500
    base["log"] = [{"at": now, "text": "%s stretched and remembered you." % base["name"]}]
    base["input"] = ""
    return apply_idle_time(base, now)


def apply_idle_time(state, now):
    elapsed_min = max(0.0, (now - state["lastTickAt"]) / 60000.0)
    if elapsed_min < 0.05:
        state["lastTickAt"] = now
        return state
    capped = min(elapsed_min, 180.0)
    sleeping = state["mood"] == "sleeping"
    state["hunger"] = clamp(state["hunger"] + capped * 0.55)
    state["happiness"] = clamp(state["happiness"] - capped * 0.22)
    state["energy"] = clamp(state["energy"] + (capped * 1.4 if sleeping else -capped * 0.18))
    if sleeping and state["energy"] > 88:
        state["mood"] = "curious"
    elif not sleeping and state["energy"] < 12:
        state["mood"] = "sleeping"
        state["pose"] = "sleep"
    elif state["hunger"] > 82:
        state["mood"] = "annoyed"
    elif state["happiness"] > 82:
        state["mood"] = "happy"
    state["lastTickAt"] = now
    return state


def _add_log(state, text, now):
    log = [{"at": now, "text": text}] + list(state.get("log") or [])
    state["log"] = log[:LOG_CAP]


def _derive_mood(state, now):
    if state["mood"] == "sleeping":
        return "sleeping"
    if state["mood"] == "playing" and now < state["poseUntil"]:
        return "playing"
    if state["energy"] < 14:
        return "sleepy"
    if state["hunger"] > 82:
        return "annoyed"
    if state["happiness"] > 84:
        return "happy"
    if now - state["lastInteractAt"] > 25000:
        return "sleepy" if state["traits"]["sleepy"] > 0.55 else "curious"
    if state["happiness"] < 28:
        return "annoyed"
    return "idle"


def tick(state, now=None, rng=random.random):
    if now is None:
        now = now_ms()
    apply_idle_time(state, now)
    mood = _derive_mood(state, now)
    state["mood"] = mood
    state["offsetX"] = state.get("offsetX", 0) * 0.82
    if abs(state["offsetX"]) < 0.15:
        state["offsetX"] = 0.0

    if mood == "sleeping":
        state["pose"] = "sleep"
        state["look"] = 0
        state["offsetX"] = 0.0
        if now >= state["thoughtUntil"]:
            state["thought"] = thought_for_mood(state, rng)
            state["thoughtUntil"] = now + 5000
        return state

    if now >= state["poseUntil"]:
        roll = rng()
        if mood == "playing":
            state["pose"] = "pounce" if roll < 0.5 else "happy"
            state["poseUntil"] = now + POSE_MED
        elif mood == "happy" and roll < 0.25:
            state["pose"] = "hearts"
            state["poseUntil"] = now + POSE_MED
        elif mood == "annoyed":
            state["pose"] = "annoyed"
            state["poseUntil"] = now + POSE_LONG
        elif mood == "sleepy" and roll < 0.35:
            state["pose"] = "yawn"
            state["poseUntil"] = now + POSE_LONG
        elif mood == "curious" and roll < 0.4:
            state["pose"] = "lookLeft" if rng() < 0.5 else "lookRight"
            state["look"] = -1 if state["pose"] == "lookLeft" else 1
            state["poseUntil"] = now + POSE_MED
        elif roll < 0.08:
            state["pose"] = CUTE_POOL[int(rng() * len(CUTE_POOL)) % len(CUTE_POOL)]
            state["poseUntil"] = now + POSE_LONG
        elif roll < 0.18:
            state["pose"] = "blink"
            state["poseUntil"] = now + 280
        elif roll < 0.4:
            state["pose"] = "earLeft" if rng() < 0.5 else "earRight"
            state["poseUntil"] = now + POSE_SHORT
        elif roll < 0.62:
            state["pose"] = "tailLeft" if rng() < 0.5 else "tailRight"
            state["poseUntil"] = now + POSE_SHORT
        else:
            state["pose"] = "sit"
            state["poseUntil"] = now + POSE_MED
            if rng() < 0.3:
                state["look"] = 0

    if now >= state["thoughtUntil"]:
        state["thought"] = thought_for_mood(state, rng)
        state["thoughtUntil"] = now + int(THOUGHT_MS + rng() * 2400)

    if (
        mood == "sleepy"
        and state["energy"] < 22
        and now - state["lastInteractAt"] > 18000
        and rng() < 0.04
    ):
        state["mood"] = "sleeping"
        state["pose"] = "sleep"
        state["poseUntil"] = now + 8000
        state["thought"] = "zzz..."
        state["thoughtUntil"] = now + 5000
        state["look"] = 0
        state["offsetX"] = 0.0
        _add_log(state, "%s curled up and fell asleep." % state["name"], now)
    return state


def _say(state, thought, pose, now, hold=POSE_MED):
    state["pose"] = pose
    state["poseUntil"] = now + hold
    state["thought"] = thought
    state["thoughtUntil"] = now + THOUGHT_MS
    state["lastInteractAt"] = now
    state["lastTickAt"] = now
    return state


def apply_action(state, kind, now=None, extra="", rng=random.random):
    if now is None:
        now = now_ms()
    apply_idle_time(state, now)
    if kind not in ("wake", "look") and state["mood"] == "sleeping":
        state["mood"] = "curious"
        state["pose"] = "blink"
        _add_log(state, "%s blinked awake." % state["name"], now)

    if kind == "pet":
        state["happiness"] = clamp(state["happiness"] + 11 + state["traits"]["clingy"] * 4)
        state["energy"] = clamp(state["energy"] + 2)
        thought = "okay, that's enough" if state["traits"]["sassy"] > 0.75 and rng() < 0.2 else "nya~ that feels nice"
        _say(state, thought, "hearts", now, POSE_LONG)
        state["mood"] = "happy"
        state["pets"] += 1
        _add_log(state, "you pet %s." % state["name"], now)
        return True, "%s leans into your hand." % state["name"]

    if kind == "feed":
        if state["hunger"] < 8:
            _say(state, "I'm full...", "annoyed", now)
            state["mood"] = "annoyed"
            return True, "%s turns away from the bowl." % state["name"]
        thought = "tuna!!" if state["hunger"] > 70 else "nom nom"
        _say(state, thought, "happy", now, POSE_LONG)
        state["hunger"] = clamp(state["hunger"] - 26)
        state["happiness"] = clamp(state["happiness"] + 7)
        state["energy"] = clamp(state["energy"] + 5)
        state["mood"] = "happy"
        state["feeds"] += 1
        _add_log(state, "you fed %s." % state["name"], now)
        return True, "%s eats like it is a secret." % state["name"]

    if kind == "play":
        if state["energy"] < 16:
            _say(state, "too tired...", "yawn", now)
            state["mood"] = "sleepy"
            return True, "%s flops over instead." % state["name"]
        _say(state, "pounce!", "pounce", now, POSE_LONG)
        state["happiness"] = clamp(state["happiness"] + 14)
        state["energy"] = clamp(state["energy"] - 16)
        state["hunger"] = clamp(state["hunger"] + 7)
        state["mood"] = "playing"
        state["plays"] += 1
        state["offsetX"] = -3 if rng() < 0.5 else 3
        _add_log(state, "you played with %s." % state["name"], now)
        return True, "%s ricochets off the furniture." % state["name"]

    if kind == "sleep":
        _say(state, "zzz...", "sleep", now, 10000)
        state["mood"] = "sleeping"
        state["look"] = 0
        _add_log(state, "%s tucked in." % state["name"], now)
        return True, "%s is out." % state["name"]

    if kind == "wake":
        if state["mood"] != "sleeping":
            return True, "%s is already up." % state["name"]
        _say(state, "mrrp?", "yawn", now)
        state["mood"] = "curious"
        _add_log(state, "you woke %s." % state["name"], now)
        return True, "%s yawns at you." % state["name"]

    if kind == "look":
        direction = -1 if extra == "left" else 1 if extra == "right" else 0
        state["look"] = direction
        state["pose"] = "lookLeft" if direction < 0 else "lookRight" if direction > 0 else "sit"
        state["poseUntil"] = now + 900
        state["offsetX"] = direction * 1.4
        state["lastInteractAt"] = now
        return True, ""

    if kind == "talk":
        thought = thought_for_talk(state, extra, rng)
        _say(state, thought, "curious", now)
        state["mood"] = "curious"
        _add_log(state, "you: %s" % extra[:48], now)
        return True, "%s listened." % state["name"]

    return False, "unknown action"


def parse_command(raw):
    text = (raw or "").strip()
    if not text:
        return "unknown", ""
    parts = text.split()
    cmd = parts[0][1:] if parts[0].startswith("/") else parts[0]
    cmd = cmd.lower()
    arg = " ".join(parts[1:])
    aliases = {
        "pet": "pet",
        "pets": "pet",
        "pat": "pet",
        "scratch": "pet",
        "feed": "feed",
        "eat": "feed",
        "food": "feed",
        "treat": "feed",
        "play": "play",
        "pounce": "play",
        "ball": "play",
        "sleep": "sleep",
        "nap": "sleep",
        "rest": "sleep",
        "wake": "wake",
        "up": "wake",
        "status": "status",
        "stats": "status",
        "info": "status",
        "help": "help",
        "?": "help",
        "h": "help",
        "name": "name",
        "rename": "name",
        "call": "name",
        "q": "quit",
        "quit": "quit",
        "exit": "quit",
    }
    if cmd in aliases:
        return aliases[cmd], arg
    if text.startswith("/"):
        return "unknown", text
    return "talk", text


def rename(state, name, now=None):
    if now is None:
        now = now_ms()
    cleaned = " ".join((name or "").split())[:16]
    if not cleaned:
        return False, "usage: name <something cute>"
    state["name"] = cleaned
    state["thought"] = "that's me?"
    state["thoughtUntil"] = now + THOUGHT_MS
    state["lastInteractAt"] = now
    _add_log(state, "now answering to %s." % cleaned, now)
    return True, "ok. %s it is." % cleaned
