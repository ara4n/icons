#!/bin/sh
# usage: scripts/render3d.sh [px=140] [seed=7] [scale=1]   -> matrix-montage-720p-3d.png (scale=2 -> matrix-montage-1440p-3d.png)
cd "$(dirname "$0")/.." && .venv/bin/python scripts/tiles.py >/dev/null 2>&1
SCALE=${3:-1}; OUT="$PWD/matrix-montage-720p-3d.png"; [ "$SCALE" = 2 ] && OUT="$PWD/matrix-montage-1440p-3d.png"
(cd render && python3 -m http.server 8765 >/dev/null 2>&1 & echo $! > /tmp/logos-srv.pid); sleep 1
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --use-angle=swiftshader --enable-unsafe-swiftshader --hide-scrollbars --window-size=1280,720 --force-device-scale-factor=$SCALE --virtual-time-budget=40000 --screenshot="$OUT" "http://localhost:8765/index.html?px=${1:-140}&seed=${2:-7}" 2>/dev/null
kill $(cat /tmp/logos-srv.pid) 2>/dev/null; true
