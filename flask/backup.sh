#!/bin/bash

FILENAME="/home/flask-app/$(date -u +%Y-%m-%dT%H:%M:%S%Z).log"

find / -type f -iname "*.app.log" -exec cat {} + 2>/dev/null > "$FILENAME"

chmod a+r "$FILENAME"
