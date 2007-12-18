#!/usr/bin/python

import cgi
import os
import time
import smtplib
import pickle

EMAIL_TO = "autotest@openlayers.org"
LOCAL_DIR = "/www/openlayers/docs/test/"



data = {}

try:
    f = open(os.path.join(LOCAL_DIR, "test_results.pickle"), "r")
    data = pickle.load(f) 
except Exception, E:
    pass

print "Content-Type: text/html"
print 
fs = cgi.FieldStorage()
if os.environ['REQUEST_METHOD'] == "POST":
    useragent = os.environ['HTTP_USER_AGENT']
    status_changed = True 
    if not data.has_key(useragent):
        data[useragent] = {}
    else:    
        old_data = data[useragent] 
        status_changed = (old_data['results'] != fs['results'].value)
    data[useragent] = {
      'time':time.time(),
      'results':fs['results'].value,
      'ip': os.environ['REMOTE_ADDR'],
      'url':''
    }  
    if fs.has_key("test_text"):
        # Failure 
        filename = "failure.%s.html"%time.time()
        error_log = open(os.path.join(LOCAL_DIR, filename), "w")
        error_log.write(fs['test_text'].value)
        error_log.close()
        data[useragent]['url'] = "http://openlayers.org/test/%s" % filename
        if status_changed:
            message = []
            message.append("From: crschmidt@metacarta.com\r\nTo: %s\r\nSubject: OpenLayers Test Failure: %s\r\n" % (EMAIL_TO, fs['results'].value))
            message.append("Results: %s" % fs['results'].value)
            message.append("URL: http://openlayers.org/test/%s" % filename)
            message.append("User-Agent: %s" % os.environ['HTTP_USER_AGENT'])
            s = smtplib.SMTP("smtp.metacarta.com")
            s.sendmail("crschmidt@metacarta.com", EMAIL_TO, "\n".join(message))
    pickle.dump(data, open(os.path.join(LOCAL_DIR, "test_results.pickle"), "w"))

print """<table>
<tr>
 <td>User-Agent</td>
 <td>IP</td>
 <td>Timestamp</td>
 <td>Results</td>
 <td>URL</td>
</tr>"""
for key in data.keys():
    print """<tr>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
 <td>%s</td>
""" % (key, data[key]['ip'], data[key]['time'], data[key]['results'])
    if data[key]['url']:
        print "<td><a href='%s'>Failure Report</a></td>" % data[key]['url']
    
    print "</tr>"    
print """</table>"""
