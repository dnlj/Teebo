import threading
import queue
import Teebo


class ReceiverThread(threading.Thread):
	def __init__(self, socket):
		super().__init__()
		
		self.sock = socket
		self.data = ""
		self.queue = queue.Queue()
		
	
	def recv(self):
		# Split into messages
		self.data += self.sock.recv(1024).decode("utf-8")
		messages = self.data.split(Teebo.eol)

		# Handler partial messages
		self.data = messages.pop()

		# Process messages
		for message in messages:
			self.queue.put(Teebo.Message(message))
			
	
	def run(self):
		while True:
			self.recv()
		
