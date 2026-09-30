#!/usr/bin/env bash
# ============================================================
# setup.sh — prepares the project for scraping
# Usage: ./setup.sh
# Creates venv, installs dependencies, and hooks up Chrome.
# ============================================================
set -e
cd "$(dirname "$0")"

echo "[1/3] Virtualenv + dependencies..."
if [ ! -d venv ]; then
  python3 -m venv venv
fi
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q -r requirements.txt

echo "[2/3] Looking for Chrome..."
CHROME=""
for c in \
  "$HOME/chrome-for-testing/chrome-linux64/chrome" \
  "$HOME/.cache/puppeteer/chrome/"*/chrome-linux64/chrome \
  "/usr/bin/google-chrome" \
  "/usr/bin/chromium"; do
  if [ -x "$c" ]; then CHROME="$c"; break; fi
done

if [ -z "$CHROME" ]; then
  echo "  x Chrome not found. Download Chrome for Testing to ~/chrome-for-testing/ and run again."
  exit 1
fi

mkdir -p "$HOME/bin"
ln -sf "$CHROME" "$HOME/bin/google-chrome"
echo "  OK Chrome: $CHROME"

echo "[3/3] Done."
echo
echo "To scrape:"
echo "  PATH=\$HOME/bin:\$PATH ./venv/bin/python maps.py -q queries.txt -w 1 -l 25 -bw 30 -sm 1 -se contacts -se about -o output"
echo "Or simply:  ./run.sh [queries-file] [output-folder]"
