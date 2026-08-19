"""Fixed-width ASCII kitten frames.

Every pose is padded to SPRITE_W x SPRITE_H so redraws never scroll the
terminal. Faces stay ASCII-safe (no fullwidth / CJK) so Termux, CMD, and
old macOS Terminal all render the same cat.
"""

from __future__ import annotations

SPRITE_W = 21
SPRITE_H = 5

POSES = (
    "sit",
    "blink",
    "lookLeft",
    "lookRight",
    "earLeft",
    "earRight",
    "tailLeft",
    "tailRight",
    "happy",
    "hearts",
    "sleep",
    "yawn",
    "annoyed",
    "curious",
    "stretch",
    "pounce",
    "groom",
)

_RAW = {
    "sit": [
        r"      /\_/\      ",
        r"     ( o.o )     ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "blink": [
        r"      /\_/\      ",
        r"     ( -.- )     ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "lookLeft": [
        r"      /\_/\      ",
        r"     (o.  )      ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "lookRight": [
        r"      /\_/\      ",
        r"     (  .o)      ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "earLeft": [
        r"      /\_/~      ",
        r"     ( o.o )     ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "earRight": [
        r"      ~\_/\      ",
        r"     ( o.o )     ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "tailLeft": [
        r"      /\_/\      ",
        r"     ( o.o )     ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"   ~(_|   |_)    ",
    ],
    "tailRight": [
        r"      /\_/\      ",
        r"     ( o.o )     ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)~   ",
    ],
    "happy": [
        r"      /\_/\      ",
        r"     ( ^.^. )    ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "hearts": [
        r"      /\_/\   *  ",
        r"     ( ^.^. )    ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "sleep": [
        r"      /\_/\      ",
        r"     ( -.- ) zzz ",
        r"      > ^ <      ",
        r"     /|___|\     ",
        r"    (_|   |_)    ",
    ],
    "yawn": [
        r"      /\_/\      ",
        r"     ( o.O )     ",
        r"      > O <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "annoyed": [
        r"      /\_/\      ",
        r"     ( -_- )     ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "curious": [
        r"      /\_/\      ",
        r"     ( o.o?)     ",
        r"      > ^ <      ",
        r"     /|   |\     ",
        r"    (_|   |_)    ",
    ],
    "stretch": [
        r"  /\         /\  ",
        r" ( - .     . - ) ",
        r"  >           <  ",
        r" ~~~~~~~~~~~~~~~ ",
        r"                 ",
    ],
    "pounce": [
        r"           /\_/\ ",
        r"          ( >o< )",
        r"           > ^ < ",
        "          /| ~ |\\",
        r"         (_| ^ |_)",
    ],
    "groom": [
        r"      /\_/\      ",
        r"     ( -.- )     ",
        r"      > ^ <      ",
        r"     /|  ~ |\    ",
        r"    (_|   |_)    ",
    ],
}

CUTE_POOL = ("stretch", "yawn", "groom", "curious", "pounce", "earLeft", "tailRight")


def pad_sprite(lines):
    out = [line.ljust(SPRITE_W)[:SPRITE_W] for line in lines]
    while len(out) < SPRITE_H:
        out.append(" " * SPRITE_W)
    return out[:SPRITE_H]


SPRITES = {name: pad_sprite(lines) for name, lines in _RAW.items()}


def sprite_lines(pose, look=0, offset_x=0):
    key = pose
    if pose == "sit":
        if look < 0:
            key = "lookLeft"
        elif look > 0:
            key = "lookRight"
    lines = SPRITES.get(key, SPRITES["sit"])
    shift = max(-6, min(6, int(round(offset_x))))
    if not shift:
        return list(lines)
    out = []
    for line in lines:
        if shift > 0:
            out.append((" " * shift + line)[:SPRITE_W])
        else:
            out.append((line + " " * (-shift))[-SPRITE_W:])
    return out


def thought_box(text, width=None):
    inner = text if len(text) <= 18 else text[:17] + "..."
    width = max(12, len(inner) + 2)
    pad = inner.ljust(width - 2)
    top = " " + ("_" * width)
    mid = "( " + pad + ")"
    bot = " " + ("-" * width)
    pointer = " " * (width // 2) + "\\"
    return [top, mid, bot, pointer]
