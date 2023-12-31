#!/bin/bash

function kill {
    pkill -f "python3 /Users/mrarab/Documents/GitHub/RailwayCrossingGates-App/main.py"
    echo "closed main.py"
}

trap kill SIGINT

while true; do
    current_hour=$(date +"%H")
    current_minute=$(date +"%M")
    time=$(date +"%H:%M:%S")
    x=$((61 + RANDOM % 14))

    # while(time != (24-3 AM))
    if [ "$current_hour" -ge 3 ] && [ "$current_hour" -lt 24 ]; then
        echo "[G: $current_hour:$current_minute] launching script. . . "
        python3 /Users/mrarab/Documents/GitHub/RailwayCrossingGates-App/main.py
        sleep 10
        kill

        echo "[$time] awaiting for assignment in $x seconds. . ."
        echo " "
        sleep $x
    else
        echo " "
        echo " <<< Time between 24:00-3:00 detected >>> "
        echo "[G: $current_hour:$current_minute] Script won't scrap the site until it's 3 AM."
        sleep $x
    fi
done