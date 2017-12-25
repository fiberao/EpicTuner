#!/usr/bin/env python

import http.server
import socketserver
import threading
PORT = 8082
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("0.0.0.0", PORT), Handler)
thread =threading.Thread(target = httpd.serve_forever)
thread.start()
print ("Mirror Visualization at: http://localhost:"+str(PORT))
import asyncio
import datetime
import random
import websockets
import time
now =[i for i in range(0,37)]

async def responder(websocket, path):
	global now
	try:
		while True:
			await websocket.send(str(now))
			await asyncio.sleep(0.1)
	except websockets.exceptions.ConnectionClosed as valerr:
		print("connection closed. ",str(valerr))

start_server = websockets.serve(responder, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
thread2 =threading.Thread(target = asyncio.get_event_loop().run_forever)
thread2.start()

def send_visual(test,max_v=50):
	global now
	now=[max_v]
	for each in test:
		now.append((1.0-each)*max_v)
