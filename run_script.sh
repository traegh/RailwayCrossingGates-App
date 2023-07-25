#!/bin/bash

function kill {
    pkill -f "python3 /Users/mrarab/Documents/GitHub/RailwayCrossingGates-App/main.py"
    echo "closed main.py "
}

trap kill SIGINT

while true; do
    echo "launching main.py... "
    python3 /Users/mrarab/Documents/GitHub/RailwayCrossingGates-App/main.py
    sleep 13
    kill
    x=$((140 + RANDOM % 10))
    time=$(date +"%H:%M:%S")
    echo "[$time] waiting till the next launch $x seconds. "
    sleep $x
done