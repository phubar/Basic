#!/usr/bin/python

import urllib, re

data = re.search('"([0-9.]*)"', urllib.urlopen("http://ip.jsontest.com/").read()).group(1)
print data
