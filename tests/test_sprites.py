#!/usr/bin/env python3
"""Sprite geometry stays a fixed box so the cursor never jumps."""

from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from kitten.sprites import POSES, SPRITE_H, SPRITE_W, SPRITES, sprite_lines, thought_box


class SpriteTests(unittest.TestCase):
    def test_every_pose_is_padded(self):
        for pose in POSES:
            self.assertIn(pose, SPRITES)
            lines = SPRITES[pose]
            self.assertEqual(len(lines), SPRITE_H)
            for line in lines:
                self.assertEqual(len(line), SPRITE_W, pose + repr(line))

    def test_look_swap_keeps_size(self):
        for look in (-1, 0, 1):
            lines = sprite_lines("sit", look=look, offset_x=look * 3)
            self.assertEqual(len(lines), SPRITE_H)
            for line in lines:
                self.assertEqual(len(line), SPRITE_W)

    def test_thought_box_shape(self):
        box = thought_box("nya~")
        self.assertGreaterEqual(len(box), 3)
        self.assertTrue(box[0].strip().startswith("_") or "_" in box[0])
        wide = thought_box("this thought is deliberately too long for the bubble")
        self.assertTrue(any(len(row) <= 24 for row in wide))


if __name__ == "__main__":
    unittest.main()
