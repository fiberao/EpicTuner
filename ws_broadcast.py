import asyncio
import datetime
import random
import websockets
import threading
import time
now =[i for i in range(0,38)]

async def responder(websocket, path):
	global now
	try:
		while True:
			await websocket.send(str(now))
			await asyncio.sleep(0.1)
	except websockets.exceptions.ConnectionClosed as valerr:
		print("connection closed. ",str(valerr))

PORT_WS = 5678
start_server = websockets.serve(responder, '0.0.0.0', PORT_WS)

asyncio.get_event_loop().run_until_complete(start_server)
thread2 =threading.Thread(target = asyncio.get_event_loop().run_forever)
thread2.start()
#0-40,60
def send_visual(test,max_v=40):
	global now
	now=[max_v+20]
	for each in test:
		now.append((1.0-each)*max_v)
