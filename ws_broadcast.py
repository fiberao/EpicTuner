import threading
import logging
import time
from websocket_server import WebsocketServer
servers={}
last_sent={}
sent_record={}
def new_port(PORT=5678):
	global last_sent
	global servers
	global sent_record
	def new_message(client, server, message):
		if (message=="update"):
			if (PORT in sent_record) and (sent_record[PORT] is not None):
				server.send_message(client,sent_record[PORT])
				print("client "+str(client["address"])+" asks for update")
		else:
			print("client "+str(client["address"])+" asks "+message)
	def new_client(client, server):
		print("New client "+str(client["address"])+" connected to port "+str(PORT)+". ")
	server = WebsocketServer(PORT, host='0.0.0.0', loglevel=logging.INFO)
	server.set_fn_new_client(new_client)
	server.set_fn_message_received(new_message)
	servers[PORT]=server
	thread2 =threading.Thread(target = server.run_forever)
	thread2.start()
#0-40,60
def send_dmview(now,PORT=5678):
	global servers
	global last_sent
	global sent_record
	sent_record[PORT]=now
	millis = int(round(time.time() * 1000))
	if (not(PORT in last_sent)) or (millis-last_sent[PORT]>100):
		# prevent sending too fast
		servers[PORT].send_message_to_all(now)
		millis = int(round(time.time() * 1000))
		last_sent[PORT]=millis

new_port()