"""Terminal capability detection and a tiny ANSI helper.

The kitten must run in Linux, macOS Terminal, Windows Terminal, PowerShell,
CMD (Windows 10+ VT), Termux, and SSH. We probe; we never assume.

If the session cannot do cursor addressing we fall back to reprinting a
compact block (a few newlines). That looks worse, but it still works.
"""

from __future__ import annotations

import os
import sys


def _env_flag(*names):
    for name in names:
        val = os.environ.get(name)
        if val:
            return val
    return ""


def enable_windows_vt():
    """Turn on ENABLE_VIRTUAL_TERMINAL_PROCESSING for Win32 consoles."""
    if os.name != "nt":
        return False
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        ENABLE_VT = 0x0004
        return bool(kernel32.SetConsoleMode(handle, mode.value | ENABLE_VT))
    except Exception:
        return False


class Term:
    def __init__(self, stream=None, force_ascii=False, force_plain=False):
        self.out = stream or sys.stdout
        self.isatty = bool(getattr(self.out, "isatty", lambda: False)())
        self.windows_vt = enable_windows_vt()
        term = (_env_flag("TERM") or "").lower()
        colorterm = _env_flag("COLORTERM").lower()
        no_color = "NO_COLOR" in os.environ
        dumb = term in ("dumb", "unknown", "")
        self.ansi = (
            (not force_plain)
            and self.isatty
            and not dumb
            and (os.name != "nt" or self.windows_vt or "WT_SESSION" in os.environ)
        )
        self.color = self.ansi and not no_color and (bool(term) or bool(colorterm) or os.name == "nt")
        encoding = getattr(self.out, "encoding", None) or "utf-8"
        self.unicode = (not force_ascii) and encoding.lower().replace("-", "") not in (
            "ascii",
            "cp437",
            "cp850",
        )
        self.cols, self.rows = self.size()

    def size(self):
        try:
            import shutil

            sz = shutil.get_terminal_size(fallback=(80, 24))
            return max(20, sz.columns), max(10, sz.lines)
        except Exception:
            return 80, 24

    def write(self, text):
        try:
            self.out.write(text)
        except UnicodeEncodeError:
            self.out.write(text.encode("ascii", "replace").decode("ascii"))

    def flush(self):
        try:
            self.out.flush()
        except Exception:
            pass

    def esc(self, code):
        if self.ansi:
            self.write("\x1b[" + code)

    def hide_cursor(self):
        self.esc("?25l")

    def show_cursor(self):
        self.esc("?25h")

    def alt_on(self):
        self.esc("?1049h")

    def alt_off(self):
        self.esc("?1049l")

    def clear(self):
        if self.ansi:
            self.esc("2J")
            self.esc("H")
        else:
            self.write("\n" * 2)

    def move(self, row, col):
        if self.ansi:
            self.esc("%d;%dH" % (row, col))

    def colorize(self, text, kind="fg"):
        if not self.color:
            return text
        codes = {"fg": "37", "dim": "90", "warm": "37", "reset": "0"}
        return "\x1b[%sm%s\x1b[0m" % (codes.get(kind, "0"), text)

    def mouse_on(self):
        # SGR mouse: clicks only. Many SSH/Termux sessions support this.
        if self.ansi:
            self.esc("?1000h")
            self.esc("?1006h")

    def mouse_off(self):
        if self.ansi:
            self.esc("?1006l")
            self.esc("?1000l")
