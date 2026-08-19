#!/usr/bin/env bash
# Install the `kitten` command into ~/.local/bin (no root, no pip required).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
TARGET="${BIN_DIR}/kitten"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  echo "  Termux:        pkg install python"
  echo "  Debian/Ubuntu: sudo apt install python3"
  echo "  macOS:         xcode-select --install   (or brew install python)"
  exit 1
fi

mkdir -p "${BIN_DIR}"

# Portable path embedding (works on bash without ${var@Q}).
python3 - "$ROOT" "$TARGET" <<'PY'
import os, sys
root, target = sys.argv[1], sys.argv[2]
content = f"""#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.join({root!r}, "src"))
from kitten.app import main

if __name__ == "__main__":
    raise SystemExit(main())
"""
with open(target, "w", encoding="utf-8") as fh:
    fh.write(content)
os.chmod(target, 0o755)
print(f"installed {target}")
PY

chmod +x "${ROOT}/kitten" 2>/dev/null || true

case ":${PATH}:" in
  *":${BIN_DIR}:"*) ;;
  *)
    echo
    echo "Add this to your shell rc so \`kitten\` is on PATH:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    ;;
esac
echo
echo "run:  kitten"
echo "help: kitten --help"
