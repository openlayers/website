#!/usr/bin/env python

"""This is a blind proxy that we use to get around browser restrictions that
prevent the Javascript from loading pages not on the same server as the
Javascript. It will only load HTTP and HTTPS requests, and it will check the
content to see if it's XML-like or tab-separated text.  If the content is
neither, the proxy will increment a semaphore in memcached keyed to that IP
address. If the IP in question exceeds its daily quota of bad requests, it will
be shut off for 24 hours from its first request."""

"""The following Apache 2 config is used to make this work:
    <Directory /www/openlayers/htdocs/proxy>
         SetHandler mod_python
         PythonHandler saferproxy
         PythonDebug On
    </Directory>
"""

from mod_python import apache, util
import urllib, time, cgi, re, warnings
import memcache

is_xml_like         = re.compile( r'^\s*<\?xml[^>]*\?>', re.DOTALL )
is_tab_separated    = re.compile( r'^(?:(?:[^\t\n]+\t)+[^\t\n]*\n?)+\s*$', 
                                    re.DOTALL )

class Session (object):
    max_bad_requests = 6
    timeout = 86400

    def __init__ (self, ip):
        self.cache = memcache.Client(['127.0.0.1:11211'], debug=0)
        self.ip    = ip

    def made_bad_request (self):
        try:
            self.cache.incr( self.ip )
        except ValueError:
            self.validate(1)

    def made_good_request (self):
        try:
            self.cache.decr( self.ip )
        except ValueError:
            pass

    def validate (self, initial = 0):
        count = self.cache.get( self.ip )
        if count is None:
            self.cache.set( self.ip, str(initial), time.time() + self.timeout )
            return True
        else:
            return int(count) < self.max_bad_requests

def handler (req):
    client = Session(req.connection.remote_ip)
    if not client.validate():
        return apache.HTTP_SERVICE_UNAVAILABLE

    fs = util.FieldStorage(req)
    url = fs["url"]
    if url.startswith("http://") or url.startswith("https://"):
        proxy = urllib.urlopen(url)
        content = proxy.read()
        proxy.close()

        content_type = None
        if is_xml_like.match(content):
            content_type = "text/xml"
        elif is_tab_separated.match(content): 
            content_type = "text/plain"

        if content_type is not None:
            req.content_type = content_type
            req.write(content)
            client.made_good_request()
            return apache.OK
        else:
            client.made_bad_request()
            return apache.HTTP_BAD_REQUEST
    else:
        client.made_bad_request()
        return apache.HTTP_BAD_REQUEST
