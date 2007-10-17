#!/usr/bin/env python

import sys, memcache

if len(sys.argv) < 2:
    print "Usage: %s <IP address>"% sys.argv[0]
else:
    cache = memcache.Client(["127.0.0.1:11211"])
    cache.delete(sys.argv[1])

