#!/usr/bin/env python

import http.server
import socketserver
import threading
import webbrowser 
import random
PORT = random.randint(10000,60000)
from http.server import SimpleHTTPRequestHandler

class CORSRequestHandler (SimpleHTTPRequestHandler):
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

httpd = socketserver.TCPServer(("127.0.0.1", PORT), CORSRequestHandler)
thread =threading.Thread(target = httpd.serve_forever)
thread.start()
URL="http://localhost:"+str(PORT)
webbrowser.open(URL)
print ("Mirror Visualization GUI at "+URL)