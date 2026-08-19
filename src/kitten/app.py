"""Main loop: draw the kitten, read keys, keep the creature alive.

Redraws the same rectangle with cursor addressing. Stats persist on
exit and every few interactions.
"""

from __future__ import annotations

import signal
import sys
import time

from . import persist
from .input import Input
from .render import build_frame, paint
from .state import HELP_LINES, apply_action, now_ms, parse_command, rename, tick
from .terminal import Term


def _handle_command(state, raw):
    kind, arg = parse_command(raw)
    if kind == "help":
        return state, "  ·  ".join(HELP_LINES[:4])
    if kind == "status":
        from .thoughts import status_lines

        return state, " | ".join(status_lines(state)[:3])
    if kind == "name":
        ok, msg = rename(state, arg)
        return state, msg
    if kind == "quit":
        return state, "__quit__"
    if kind == "talk":
        _, msg = apply_action(state, "talk", extra=arg)
        return state, msg
    if kind == "unknown":
        return state, "unknown command. try help"
    _, msg = apply_action(state, kind, extra=arg)
    return state, msg


def run(speed=1.0, force_ascii=False, force_plain=False, reset=False):
    if reset:
        persist.reset()
    term = Term(force_ascii=force_ascii, force_plain=force_plain)
    state = persist.load()
    flash = "%s is here. type help." % state["name"]
    last_save = time.time()
    dirty = True
    running = True

    def stop(_signum=None, _frame=None):
        nonlocal running
        running = False

    prev_int = signal.getsignal(signal.SIGINT)
    prev_term = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    if hasattr(signal, "SIGWINCH"):

        def on_winch(_s, _f):
            nonlocal dirty
            dirty = True

        signal.signal(signal.SIGWINCH, on_winch)

    interval = max(0.05, 0.18 / max(0.4, min(3.0, speed)))

    try:
        if term.ansi:
            term.alt_on()
            term.hide_cursor()
            term.clear()
            term.mouse_on()
        with Input() as keys:
            while running:
                t0 = time.time()
                tick(state, now_ms())
                events = keys.events(timeout=interval)
                for ev in events:
                    dirty = True
                    typ = ev.get("type")
                    if typ == "ctrl" and ev.get("key") in ("c", "d"):
                        running = False
                        break
                    if typ == "esc":
                        running = False
                        break
                    if typ == "click":
                        apply_action(state, "wake" if state["mood"] == "sleeping" else "pet")
                        flash = "you reached out."
                        continue
                    if typ == "arrow":
                        if ev.get("dir") in ("left", "right"):
                            apply_action(state, "look", extra=ev["dir"])
                        continue
                    if typ == "backspace":
                        state["input"] = (state.get("input") or "")[:-1]
                        continue
                    if typ == "enter":
                        raw = (state.get("input") or "").strip()
                        state["input"] = ""
                        if raw:
                            state, msg = _handle_command(state, raw)
                            if msg == "__quit__":
                                running = False
                                break
                            flash = msg
                        continue
                    if typ == "char":
                        key = ev.get("key") or ""
                        if key and len(state.get("input") or "") < 48:
                            state["input"] = (state.get("input") or "") + key
                paint(term, build_frame(state, term.cols, term.rows, flash))
                dirty = False
                if time.time() - last_save > 8:
                    persist.save(state)
                    last_save = time.time()
                spent = time.time() - t0
                if spent < interval * 0.25:
                    time.sleep(max(0.0, interval - spent))
    finally:
        persist.save(state)
        term.mouse_off()
        term.show_cursor()
        term.alt_off()
        if not term.ansi:
            term.write("\nbye.\n")
        term.flush()
        try:
            signal.signal(signal.SIGINT, prev_int)
            signal.signal(signal.SIGTERM, prev_term)
        except Exception:
            pass
    return 0


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    speed = 1.0
    force_ascii = False
    force_plain = False
    reset = False
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            sys.stdout.write(
                "nya — a tiny terminal kitten\n\n"
                "  kitten              run\n"
                "  kitten --speed 1.5  faster idle animation\n"
                "  kitten --ascii      force ASCII-only glyphs\n"
                "  kitten --plain      disable ANSI (scroll fallback)\n"
                "  kitten --reset      forget the saved kitten\n"
            )
            return 0
        if arg == "--speed" and i + 1 < len(argv):
            try:
                speed = float(argv[i + 1])
            except ValueError:
                speed = 1.0
            i += 2
            continue
        if arg == "--ascii":
            force_ascii = True
        elif arg == "--plain":
            force_plain = True
        elif arg == "--reset":
            reset = True
        i += 1
    try:
        return run(speed=speed, force_ascii=force_ascii, force_plain=force_plain, reset=reset)
    except KeyboardInterrupt:
        return 0
