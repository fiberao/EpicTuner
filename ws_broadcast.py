import threading
import logging
import time
from websocket_server import WebsocketServer
class broadcast:
	def __init__(self,PORT=5678):
		self.last_sent=None
		self.sent_record=None
		def new_message(client, server, message):
			if (message=="update"):
				if (sent_record is not None):
					server.send_message(client,sent_record)
					print("client "+str(client["address"])+" asks for update")
			else:
				print("client "+str(client["address"])+" asks "+message)
		def new_client(client, server):
			print("New client "+str(client["address"])+" connected to port "+str(PORT)+". ")
		self.server = WebsocketServer(PORT, host='0.0.0.0', loglevel=logging.INFO)
		self.server.set_fn_new_client(new_client)
		self.server.set_fn_message_received(new_message)

		thread2 =threading.Thread(target = self.server.run_forever)
		thread2.daemon=True
		thread2.start()
	def send(self,now):
		self.sent_record=now
		millis = int(round(time.time() * 1000))
		if (self.last_sent is None) or (millis-self.last_sent>100):
			# prevent sending too fast
			self.server.send_message_to_all(now)
			millis = int(round(time.time() * 1000))
			self.last_sent=millis
