# Nya — a tiny terminal kitten

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A living ASCII companion that sits in your terminal, blinks, stretches,
falls asleep, and reacts to what you type. **Zero third-party packages.**
Python 3.8+ only.

**Repository:** https://github.com/aditya4f/Nya-theKitten

```
        ______________
       (  nya~        )
        --------------
               \
            /\_/\
           ( o.o )
            > ^ <
           /|   |\
          (_|   |_)
```

---

## Quick start

```bash
git clone https://github.com/aditya4f/Nya-theKitten.git
cd Nya-theKitten
chmod +x install.sh kitten
./install.sh
kitten
```

Or run without installing:

```bash
./kitten
# or
PYTHONPATH=src python3 -m kitten
```

---

## Install by OS

### Linux

```bash
# Python 3 is usually already installed (Debian/Ubuntu/Fedora/Arch).
git clone https://github.com/aditya4f/Nya-theKitten.git
cd Nya-theKitten
chmod +x install.sh kitten
./install.sh
kitten
```

If `python3` is missing:

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install -y python3 git

# Fedora
sudo dnf install -y python3 git

# Arch
sudo pacman -S python git
```

### macOS

```bash
# Xcode CLT or Homebrew Python is fine.
git clone https://github.com/aditya4f/Nya-theKitten.git
cd Nya-theKitten
chmod +x install.sh kitten
./install.sh
kitten
```

Optional with Homebrew:

```bash
brew install python git
```

### Windows (Windows Terminal, PowerShell, CMD)

1. Install **Python 3** from https://www.python.org/downloads/  
   (check **“Add python.exe to PATH”** during setup).
2. Open **PowerShell** or **Windows Terminal**:

```powershell
git clone https://github.com/aditya4f/Nya-theKitten.git
cd Nya-theKitten
python .\kitten
```

Windows 10+ enables ANSI via Virtual Terminal processing at startup.
**Windows Terminal** is recommended; stock CMD works for the basics.

### Termux (Android)

```bash
pkg update
pkg install python git
git clone https://github.com/aditya4f/Nya-theKitten.git
cd Nya-theKitten
chmod +x install.sh kitten
./install.sh
kitten
```

If `kitten` is not found after install:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
kitten
```

### SSH / remote servers

Same as Linux. Clone on the remote host, run `./kitten`. Works over SSH
when the remote `TERM` is not `dumb`.

---

## Commands

Type a command and press Enter. A leading `/` is optional.

| command   | what happens                    |
|-----------|---------------------------------|
| `pet`     | scratch behind the ears         |
| `feed`    | offer a snack                   |
| `play`    | toss something shiny            |
| `sleep`   | dim the lights                  |
| `wake`    | rustle the blanket              |
| `status`  | inspect hunger / happy / energy |
| `name x`  | give the kitten a new name      |
| `help`    | list commands                   |
| `q`       | leave quietly                   |

Anything else is conversation — the kitten answers in the thought box.
Arrow keys look around. A mouse click (when the terminal supports SGR
mouse) is a pet. Ctrl+C restores the cursor and the previous screen.

Flags:

```
kitten --speed 1.5   faster idle animation
kitten --ascii       force ASCII-only glyphs
kitten --plain       disable ANSI (reprint fallback)
kitten --reset       forget the saved kitten
```

---

## How it feels alive

The kitten is a small state machine, not a GIF.

- Idle animations: blink, ear twitch, tail flick, look around
- Occasional stretch, yawn, groom, or pounce
- Moods: idle, happy, curious, sleepy, excited, annoyed, playing, sleeping
- Hunger / happiness / energy drift in real time, including while you are away
- Falls asleep if ignored; wakes when you pet, feed, or talk
- Persistent personality traits (clingy / sassy / sleepy) colour the dialogue
- Stats survive between sessions

State file:

- Linux / macOS / Termux: `~/.config/terminal-kitten/state.json`
- Windows: `%APPDATA%\\terminal-kitten\\state.json`

---

## Terminal notes

Nya probes the session instead of assuming capabilities.

- ANSI alternate screen + cursor addressing when `TERM` is not `dumb`
- Colour is skipped when `NO_COLOR` is set
- Windows VT mode is turned on through `kernel32` when needed
- Tiny terminals still get a clipped but readable frame
- Unsupported hosts fall back to reprinting a compact block
- SIGINT / SIGTERM restore the cursor, mouse, and original screen

---

## Tests

```bash
python3 -m unittest discover -s tests -v
```

No network, no TTY, no extra packages.

---

## Project layout

```
Nya-theKitten/
├── src/kitten/          state, sprites, render, input, terminal
├── tests/               state / sprite / input tests
├── install.sh
├── kitten               launcher
├── pyproject.toml
└── README.md
```

---

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Created with [Grok](https://grok.com) (xAI) from a single prompt.</sub>
