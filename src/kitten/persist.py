"""Save / load kitten stats between sessions.

Path: $XDG_CONFIG_HOME/terminal-kitten/state.json
   or ~/.config/terminal-kitten/state.json
   or %APPDATA%\\terminal-kitten\\state.json on Windows
"""

from __future__ import annotations

import json
import os

from .state import create_kitten, hydrate, snapshot


def config_dir():
    if os.name == "nt":
        root = os.environ.get("APPDATA") or os.path.expanduser("~")
        return os.path.join(root, "terminal-kitten")
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return os.path.join(xdg, "terminal-kitten")
    return os.path.join(os.path.expanduser("~"), ".config", "terminal-kitten")


def state_path():
    return os.path.join(config_dir(), "state.json")


def load(now=None):
    path = state_path()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict) or "name" not in data:
            return create_kitten(now=now)
        return hydrate(data, now)
    except FileNotFoundError:
        return create_kitten(now=now)
    except (OSError, ValueError, TypeError):
        return create_kitten(now=now)


def save(state):
    directory = config_dir()
    try:
        os.makedirs(directory, exist_ok=True)
        path = state_path()
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(snapshot(state), fh, indent=2)
        os.replace(tmp, path)
        return True
    except OSError:
        return False


def reset():
    path = state_path()
    try:
        if os.path.exists(path):
            os.remove(path)
        return True
    except OSError:
        return False
