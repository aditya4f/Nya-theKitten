"""Non-blocking keyboard (and optional mouse) input.

Unix: termios + tty raw mode, select() with a short timeout.
Windows: msvcrt.kbhit / getwch.

Arrow keys, backspace, enter, printable chars, Ctrl+C, and SGR mouse
clicks are decoded into small event dicts.
"""

from __future__ import annotations

import os
import sys


class Input:
    def __init__(self, stdin=None):
        self.stdin = stdin or sys.stdin
        self.fd = None
        self.old = None
        self.unix = os.name != "nt"
        try:
            self.fd = self.stdin.fileno()
        except Exception:
            self.fd = None

    def __enter__(self):
        if self.unix and self.fd is not None and self.stdin.isatty():
            import termios
            import tty

            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
        return self

    def __exit__(self, *exc):
        self.restore()

    def restore(self):
        if self.unix and self.fd is not None and self.old is not None:
            import termios

            try:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
            except Exception:
                pass
            self.old = None

    def _read_unix(self, timeout):
        if self.fd is None:
            return ""
        import select

        ready, _, _ = select.select([self.stdin], [], [], timeout)
        if not ready:
            return ""
        try:
            return os.read(self.fd, 32).decode("utf-8", "ignore")
        except Exception:
            return ""

    def _read_win(self, timeout):
        try:
            import msvcrt
            import time

            end = time.time() + timeout
            buf = []
            while time.time() < end:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in ("\x00", "\xe0") and msvcrt.kbhit():
                        code = msvcrt.getwch()
                        mapping = {"K": "\x1b[D", "M": "\x1b[C", "H": "\x1b[A", "P": "\x1b[B"}
                        buf.append(mapping.get(code, ""))
                    else:
                        buf.append(ch)
                    while msvcrt.kbhit():
                        buf.append(msvcrt.getwch())
                    break
                time.sleep(0.01)
            return "".join(buf)
        except Exception:
            return ""

    def read(self, timeout=0.08):
        if self.unix:
            return self._read_unix(timeout)
        return self._read_win(timeout)

    def events(self, timeout=0.08):
        raw = self.read(timeout)
        if not raw:
            return []
        return decode_keys(raw)


def decode_keys(raw):
    """Turn a raw byte-string of keypresses into event dicts."""
    events = []
    i = 0
    n = len(raw)
    while i < n:
        ch = raw[i]
        # SGR mouse: ESC [ < b ; x ; y M/m
        if raw.startswith("\x1b[<", i):
            j = i + 3
            while j < n and raw[j] not in "Mm":
                j += 1
            if j < n:
                body = raw[i + 3 : j]
                parts = body.split(";")
                if len(parts) == 3 and parts[0] == "0" and raw[j] == "M":
                    events.append({"type": "click", "x": _int(parts[1]), "y": _int(parts[2])})
                i = j + 1
                continue
        if raw.startswith("\x1b[A", i) or raw.startswith("\x1bOA", i):
            events.append({"type": "arrow", "dir": "up"})
            i += 3
            continue
        if raw.startswith("\x1b[B", i) or raw.startswith("\x1bOB", i):
            events.append({"type": "arrow", "dir": "down"})
            i += 3
            continue
        if raw.startswith("\x1b[C", i) or raw.startswith("\x1bOC", i):
            events.append({"type": "arrow", "dir": "right"})
            i += 3
            continue
        if raw.startswith("\x1b[D", i) or raw.startswith("\x1bOD", i):
            events.append({"type": "arrow", "dir": "left"})
            i += 3
            continue
        if ch in ("\x03",):
            events.append({"type": "ctrl", "key": "c"})
            i += 1
            continue
        if ch in ("\x04",):
            events.append({"type": "ctrl", "key": "d"})
            i += 1
            continue
        if ch in ("\r", "\n"):
            events.append({"type": "enter"})
            i += 1
            continue
        if ch in ("\x7f", "\b"):
            events.append({"type": "backspace"})
            i += 1
            continue
        if ch == "\x1b":
            events.append({"type": "esc"})
            i += 1
            continue
        if ch == "\x0c":
            events.append({"type": "ctrl", "key": "l"})
            i += 1
            continue
        if ch.isprintable():
            events.append({"type": "char", "key": ch})
        i += 1
    return events


def _int(value):
    try:
        return int(value)
    except Exception:
        return 0
