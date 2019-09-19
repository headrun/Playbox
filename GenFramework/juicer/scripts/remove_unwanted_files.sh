#!/usr/bash

var=$(locate */GenFramework*/processed  */OUTBOUND*/processed */OUTBOUND_V2*/processed */OUTBOUND_V2*/un-processed)

for each in $var;
    do
        echo "$each"
        find $each -mtime +15 -exec rm -rf *.queries {} \;
    done
