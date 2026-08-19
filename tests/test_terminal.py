#!/usr/bin/env python3
"""Input decoding and frame composition — still no live TTY required."""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from kitten.input import decode_keys
from kitten.render import build_frame
from kitten.state import create_kitten
from kitten.terminal import Term


class InputTests(unittest.TestCase):
    def test_arrows(self):
        evs = decode_keys("\x1b[D\x1b[C")
        self.assertEqual([e["dir"] for e in evs], ["left", "right"])

    def test_enter_and_backspace(self):
        evs = decode_keys("a\x7f\r")
        types = [e["type"] for e in evs]
        self.assertEqual(types, ["char", "backspace", "enter"])

    def test_ctrl_c(self):
        evs = decode_keys("\x03")
        self.assertEqual(evs[0]["type"], "ctrl")
        self.assertEqual(evs[0]["key"], "c")

    def test_mouse_sgr_click(self):
        evs = decode_keys("\x1b[<0;12;8M")
        self.assertEqual(evs[0]["type"], "click")
        self.assertEqual(evs[0]["x"], 12)

    def test_printables(self):
        evs = decode_keys("pet")
        self.assertEqual([e["key"] for e in evs], list("pet"))


class RenderTests(unittest.TestCase):
    def test_frame_is_bounded(self):
        k = create_kitten(now=1)
        lines = build_frame(k, cols=40, rows=20)
        self.assertGreaterEqual(len(lines), 10)
        self.assertLessEqual(len(lines), 20)
        for row in lines:
            self.assertLessEqual(len(row), 40)

    def test_plain_term_does_not_crash(self):
        term = Term(force_plain=True)
        self.assertFalse(term.ansi)


if __name__ == "__main__":
    unittest.main()
