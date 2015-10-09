#!/usr/bin/python

import urllib, json

data = json.loads(urllib.urlopen("http://ip.jsontest.com/").read())
