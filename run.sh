#!/usr/bin/env bash
# ============================================================
# run.sh — runs the scraper with the recommended configuration
# Usage: ./run.sh [queries.txt] [output-folder]
# Gentle config (1 thread, 30s wait) to avoid Google blocking.
# ============================================================
set -e
cd "$(dirname "$0")"

QUERIES="${1:-queries.txt}"
OUT="${2:-output}"
mkdir -p "$OUT" logs

if [ ! -x venv/bin/python ]; then
  echo "Missing venv. Run ./setup.sh first."
  exit 1
fi

LOG="logs/run_$(date +%Y%m%d_%H%M%S).log"
echo "Queries: $QUERIES | Output: $OUT | Log: $LOG"
PATH="$HOME/bin:$PATH" ./venv/bin/python maps.py \
  -q "$QUERIES" \
  -w 1 -l 25 -bw 30 -sm 1 \
  -u "Not Available" \
  -se contacts -se about \
  -o "$OUT" 2>&1 | tee "$LOG"
