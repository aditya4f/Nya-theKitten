#!/usr/bin/env python3
"""State machine tests — no TTY required."""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from kitten.state import apply_action, apply_idle_time, create_kitten, parse_command, rename, tick


class StateTests(unittest.TestCase):
    def test_create_defaults(self):
        k = create_kitten("Mochi", now=1_000)
        self.assertEqual(k["name"], "Mochi")
        self.assertGreater(k["happiness"], 0)
        self.assertIn(
            k["mood"],
            ("idle", "happy", "curious", "sleepy", "excited", "annoyed", "playing", "sleeping"),
        )

    def test_pet_raises_happiness(self):
        k = create_kitten(now=1_000)
        before = k["happiness"]
        apply_action(k, "pet", now=2_000, rng=lambda: 0.0)
        self.assertGreater(k["happiness"], before)
        self.assertEqual(k["pets"], 1)
        self.assertEqual(k["pose"], "hearts")

    def test_feed_lowers_hunger(self):
        k = create_kitten(now=1_000)
        k["hunger"] = 60
        apply_action(k, "feed", now=2_000)
        self.assertLess(k["hunger"], 60)
        self.assertEqual(k["feeds"], 1)

    def test_feed_when_full_is_annoyed(self):
        k = create_kitten(now=1_000)
        k["hunger"] = 2
        apply_action(k, "feed", now=2_000)
        self.assertEqual(k["mood"], "annoyed")

    def test_play_costs_energy(self):
        k = create_kitten(now=1_000)
        k["energy"] = 80
        apply_action(k, "play", now=2_000)
        self.assertLess(k["energy"], 80)
        self.assertEqual(k["mood"], "playing")

    def test_play_when_exhausted(self):
        k = create_kitten(now=1_000)
        k["energy"] = 5
        apply_action(k, "play", now=2_000)
        self.assertEqual(k["mood"], "sleepy")

    def test_sleep_and_wake(self):
        k = create_kitten(now=1_000)
        apply_action(k, "sleep", now=2_000)
        self.assertEqual(k["mood"], "sleeping")
        apply_action(k, "wake", now=3_000)
        self.assertNotEqual(k["mood"], "sleeping")

    def test_interact_wakes_sleeper(self):
        k = create_kitten(now=1_000)
        apply_action(k, "sleep", now=2_000)
        apply_action(k, "pet", now=3_000, rng=lambda: 0.0)
        self.assertNotEqual(k["mood"], "sleeping")

    def test_idle_time_increases_hunger(self):
        k = create_kitten(now=1_000)
        k["lastTickAt"] = 1_000
        before = k["hunger"]
        apply_idle_time(k, 1_000 + 30 * 60 * 1000)
        self.assertGreater(k["hunger"], before)

    def test_tick_blinks_or_idles(self):
        k = create_kitten(now=1_000)
        k["poseUntil"] = 0
        k["thoughtUntil"] = 10_000
        tick(k, now=5_000, rng=lambda: 0.15)
        self.assertIn(
            k["pose"],
            (
                "blink",
                "sit",
                "earLeft",
                "earRight",
                "tailLeft",
                "tailRight",
                "stretch",
                "yawn",
                "groom",
                "curious",
                "pounce",
                "hearts",
                "annoyed",
                "lookLeft",
                "lookRight",
                "happy",
                "sleep",
            ),
        )

    def test_parse_commands(self):
        self.assertEqual(parse_command("/pet")[0], "pet")
        self.assertEqual(parse_command("feed")[0], "feed")
        self.assertEqual(parse_command("hello there")[0], "talk")
        self.assertEqual(parse_command("/nope")[0], "unknown")
        self.assertEqual(parse_command("name Bean")[1], "Bean")

    def test_rename(self):
        k = create_kitten(now=1_000)
        ok, msg = rename(k, "  Bean  ", now=2_000)
        self.assertTrue(ok)
        self.assertEqual(k["name"], "Bean")
        ok, _ = rename(k, "   ", now=3_000)
        self.assertFalse(ok)

    def test_look(self):
        k = create_kitten(now=1_000)
        apply_action(k, "look", now=2_000, extra="left")
        self.assertEqual(k["look"], -1)
        apply_action(k, "look", now=3_000, extra="right")
        self.assertEqual(k["look"], 1)


if __name__ == "__main__":
    unittest.main()
