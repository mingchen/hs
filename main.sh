#!/bin/sh

if [ ! -f cisco-umbrella-top1m.txt ]; then
    echo "Downloading Cisco Umbrella Top 1M hosts"
    rm -f top-1m.csv.zip
    wget -q http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip
    unzip top-1m.csv.zip
    awk -F, '{ print $2 }' top-1m.csv > cisco-umbrella-top1m.txt
    dos2unix cisco-umbrella-top1m.txt
fi

ulimit -n

MAX_EXEC_TIME==21000 # in seconds

timeout -k 10 $MAX_EXEC_TIME ./process.py
ret=$?
echo "timeout exit code: $ret"

./dbimport.py

