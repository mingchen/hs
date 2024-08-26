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

timeout -k 10 21000 ./process.py

./dbimport.py
