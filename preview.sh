#!/usr/bin/env bash
# Opens the Bamford Lab site properly, in a local web server.
#
# Why this exists: the site uses absolute asset paths (/assets/...), which a browser
# can only resolve when the pages are SERVED. Opening _site/index.html directly gives
# you a file:// URL, the stylesheet and images never load, and the page looks broken.
# Run this instead. Double-clicking it works too (choose "Run in Terminal").

set -e
cd "$(dirname "$0")"

URL="http://localhost:8080"

is_up() { curl -s -o /dev/null --max-time 2 "$URL" 2>/dev/null; }

if is_up; then
    echo "Preview server already running."
else
    echo "Starting the preview server..."
    npm run dev >/tmp/bamford-lab-preview.log 2>&1 &
    for _ in $(seq 1 40); do
        sleep 0.5
        if is_up; then break; fi
    done
    if ! is_up; then
        echo "Server did not start. Check /tmp/bamford-lab-preview.log for the reason."
        exit 1
    fi
    echo "Started."
fi

echo "Opening $URL"
# Firefox: ask the running browser for a new TAB. Plain xdg-open passes a bare URL,
# which this Firefox setup treats as "open a new window".
if command -v firefox >/dev/null 2>&1; then
    firefox --new-tab "$URL" >/dev/null 2>&1 &
else
    xdg-open "$URL" >/dev/null 2>&1 || echo "Open $URL in your browser."
fi
echo
echo "The site reloads automatically as you edit. Leave this running."
echo "Press Ctrl+C to stop it."
wait
