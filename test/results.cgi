#!/usr/bin/python

import cgi
import os
import time
import smtplib

EMAIL_TO = "crschmidt@metacarta.com"
LOCAL_DIR = "/www/openlayers/docs/test/"

fs = cgi.FieldStorage()
if os.environ['REQUEST_METHOD'] == "POST":
    f = open(os.path.join(LOCAL_DIR, "test.log"), "a")
    f.write("User-Agent: %s\nTimestamp: %s\nResults:%s\n" % (os.environ['HTTP_USER_AGENT'], time.time(), fs['results'].value))
    if fs.has_key("test_text"):
        # FailureL 
        filename = "failure.%s.html"%time.time()
        data = open(os.path.join(LOCAL_DIR, filename), "w")
        data.write(fs['test_text'].value)
        data.close()
        f.write("http://openlayers.org/test/%s\n" % filename)
        message = []
        message.append("From: crschmidt@metacarta.com\r\nTo: EMAIL_TO\r\nSubject: OpenLayers Test Failure: %s\r\n" % fs['results'].value)
        message.append("Results: %s" % fs['results'].value)
        message.append("URL: http://openlayers.org/test/%s" % filename)
        message.append("User-Agent: %s" % os.environ['HTTP_USER_AGENT'])
        s = smtplib.SMTP("smtp.metacarta.com")
        s.sendmail("crschmidt@metacarta.com", "crschmidt@metacarta.com", "\n".join(message))
    f.write("\n")    
    f.close()
f = open(os.path.join(LOCAL_DIR, "test.log"), "r")
print "Content-Type: text/plain"
print 
print f.read()
f.close()
