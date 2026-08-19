# Nya — a tiny terminal kitten

A living ASCII companion that sits in your terminal, blinks, stretches,
falls asleep, and reacts to what you type. Zero third-party packages.
Python 3.8+ only.

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

## Install

```bash
git clone https://github.com/aditya4f/Nya-theKitten.git
cd Nya-theKitten
chmod +x install.sh kitten
./install.sh
kitten
```

Or skip the installer and run from the folder:

```bash
./kitten
# or
PYTHONPATH=src python3 -m kitten
```

### Termux (Android)

```bash
pkg update
pkg install python git
git clone https://github.com/aditya4f/Nya-theKitten.git
cd Nya-theKitten
./install.sh
kitten
```

If `kitten` is not found:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Linux

```bash
# Debian / Ubuntu / Fedora already have python3.
./install.sh
kitten
```

### macOS

```bash
# Xcode CLT or Homebrew python is fine.
./install.sh
kitten
```

### Windows (Windows Terminal, PowerShell, CMD)

1. Install Python 3 from https://www.python.org/downloads/ (tick “Add to PATH”).
2. In PowerShell, from this folder:

```powershell
python .\kitten
```

Windows 10+ consoles get ANSI via Virtual Terminal processing (enabled at
startup). Windows Terminal is the nicest host; stock CMD works for the basics.

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
- Windows: `%APPDATA%\terminal-kitten\state.json`

## Terminal notes

Nya probes the session instead of assuming capabilities.

- ANSI alternate screen + cursor addressing when `TERM` is not `dumb`
- Colour is skipped when `NO_COLOR` is set
- Windows VT mode is turned on through `kernel32` when needed
- Tiny terminals still get a clipped but readable frame
- Unsupported hosts fall back to reprinting a compact block
- SIGINT / SIGTERM restore the cursor, mouse, and original screen

## Tests

```bash
python3 -m unittest discover -s tests -v
```

No network, no TTY, no extra packages.

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

## License

MIT — see [LICENSE](LICENSE).
