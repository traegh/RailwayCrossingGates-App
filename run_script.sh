#!/bin/bash

function kill {
    pkill -f "python3 /Users/mrarab/Documents/GitHub/RailwayCrossingGates-App/main.py"
    echo "closed main.py"
}

trap kill SIGINT

while true; do
    current_hour=$(date +"%H")

    # while(time != (24-3 AM))
    if [ "$current_hour" -ge 3 ] && [ "$current_hour" -lt 24 ]; then
        echo "[G: $current_hour] launching main.py... "
        python3 /Users/mrarab/Documents/GitHub/RailwayCrossingGates-App/main.py
        sleep 10
        kill
        x=$((140 + RANDOM % 10))
        time=$(date +"%H:%M:%S")
        echo "[$time] awaiting for my work in $x seconds. . . "
        sleep $x
    else
        echo "[G: $current_hour] Maintenance. Time between 24:00-3:00 detected, script will continue sometime later."
    fi
done