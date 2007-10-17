#!/usr/bin/python

import os
import subprocess
import cgi
import sys

fs = cgi.FieldStorage()
if (fs.has_key('passwd')):
    print "Content-Type: text/plain"
    print
    sys.stdout.flush()
    subprocess.call(['/usr/bin/htpasswd', 
                       '-nb', fs['user'].value, fs['passwd'].value])
else:
    print "Content-Type: text/html"
    print
    print """<form method="POST">Username: <input name="user" /><br />
    Password: <input name="passwd" type="password" /><br />
    <input type="submit" value="Create password" />
    """
