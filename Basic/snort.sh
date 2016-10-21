#!/bin/bash

#install prereqs
yum install epel-release
yum update
yum install gcc flex bison zlib zlib-devel libpcap libpcap-devel pcre pcre-devel libdnet libdnet-devel tcpdump

#install daq and snort (from latest for centos)
yum install https://www.snort.org/downloads/snort/daq-2.0.6-1.centos7.x86_64.rpm
yum install https://www.snort.org/downloads/snort/snort-2.9.8.3-1.centos7.x86_64.rpm

#install ruleset - download latest from snort.org
tar -xvzf snortrules-snapshot-2976.tar.gz -C /etc/snort/rules
