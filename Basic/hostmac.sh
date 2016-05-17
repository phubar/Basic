#!/bin/bash

### BEGIN INIT INFO
# Provides: randhostnamemac
# Randomises hostname and MAC
# placed in /etc/init.d.
### END INIT INFO

#create hosts.old if not there

if [ ! -a /etc/hosts.old ]; then
cp /etc/hosts /etc/hosts.old
fi

#assign the variable newhn a random value as defined below

newhn=$(cat /dev/urandom | tr -dc 'A-Za-z' | head -c8)
#update hostname and hosts with new value
echo $newhn > /etc/hostname
echo "127.0.1.1 $newhn" > /etc/hosts
cat /etc/hosts.old >> /etc/hosts

#update uci

uci set system.@system[0].hostname=$newhn
uci commit system
echo $(uci get system.@system[0].hostname) > /proc/sys/kernel/hostname

#randomise MAC for wlan0 and wlan1

ifconfig wlan0 down

ifconfig wlan1 down

macchanger -A wlan0

macchanger -A wlan1

ifconfig wlan0 up

ifconfig wlan1 up

exit

