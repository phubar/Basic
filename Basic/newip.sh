#!/bin/bash
source ip.log
NEWIP=`curl -s checkip.dyndns.org | sed -e 's/.*Current IP Address: //' -e 's/<.*$//'`
if [ "$IP" != "$NEWIP" ];
	echo $NEWIP | mail -s "NEW IP" email@address.com
	echo "IP="$NEWIP > ip.log
fi
