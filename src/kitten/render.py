"""Compose a frame and paint it in-place.

The frame is always the same number of rows. We home the cursor and
overwrite so the kitten stays put instead of flooding the scrollback.
"""

from __future__ import annotations

from .sprites import SPRITE_H, sprite_lines, thought_box
from .thoughts import meter_bar


def build_frame(state, cols, rows, status_flash=""):
    name = state.get("name", "Mochi")
    mood = state.get("mood", "idle")
    thought = thought_box(state.get("thought") or "...")
    cat = sprite_lines(state.get("pose", "sit"), state.get("look", 0), state.get("offsetX", 0))
    typed = state.get("input") or ""
    caret = typed + "_"

    hunger = 100 - float(state.get("hunger", 0))
    lines = []
    lines.append("nya · %s · %s" % (name, mood))
    lines.append(
        "full %s  happy %s  energy %s"
        % (
            meter_bar(hunger, 8),
            meter_bar(state.get("happiness", 0), 8),
            meter_bar(state.get("energy", 0), 8),
        )
    )
    lines.append("")
    block = thought + [""] + cat
    width = max(len(s) for s in block)
    pad = max(0, (min(cols, 48) - width) // 2)
    prefix = " " * pad
    for row in block:
        lines.append(prefix + row)
    lines.append("")
    lines.append("nya> " + caret)
    if status_flash:
        lines.append(status_flash[: max(12, cols - 2)])
    else:
        log = state.get("log") or []
        lines.append((log[0]["text"] if log else "type help · q to leave")[: max(12, cols - 2)])
    lines.append("pet  feed  play  sleep  status")
    target = min(max(18, SPRITE_H + 12), max(12, rows - 1))
    if len(lines) < target:
        lines.extend([""] * (target - len(lines)))
    return [row[:cols] for row in lines[:target]]


def paint(term, lines):
    term.cols, term.rows = term.size()
    if term.ansi:
        term.move(1, 1)
        for i, row in enumerate(lines):
            term.move(i + 1, 1)
            padded = row.ljust(term.cols)[: term.cols]
            term.write(padded)
        term.esc("J")
    else:
        term.write("\n" + "\n".join(lines) + "\n")
    term.flush()
