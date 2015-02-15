#!/usr/bin/env python

import BaseHTTPServer
import SimpleHTTPServer
import time
import sys


HOST_NAME = sys.argv[1]
PORT_NUMBER = 8080

class RedirectHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_HEAD(s):
        if s.path == '/' or s.path == '/index.html':
            s.send_response(302)
            s.send_header("Location", '/en/')
            s.end_headers()
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_HEAD(s)

    def do_GET(s):
        if s.path == '/' or s.path == '/index.html':
            s.send_response(302)
            s.send_header("Location", '/en/')
            s.end_headers()
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(s)

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), RedirectHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
