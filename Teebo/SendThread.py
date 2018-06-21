import threading
import queue
import time
import Teebo


class SendThread(threading.Thread):
	def __init__(self, socket):
		super().__init__()
		
		self.sock = socket
		self.queue = queue.Queue()
		self.maxMessagesPerSecond = 20
		self.sentMessageCount = 0
		self.messageTime = time.perf_counter()
		
	
	def updateMessageTime(self):
		curTime = time.perf_counter()
		if (curTime - self.messageTime) >= 1.0:
			self.messageTime = curTime
			self.sentMessageCount = 0
			
	
	def send(self):
		# Wait until we can send a message
		self.updateMessageTime()
		
		while self.sentMessageCount >= self.maxMessagesPerSecond:
			time.sleep((1 + self.messageTime) - time.perf_counter())
			self.updateMessageTime()
		
		message = self.queue.get()
		
		Teebo.log("SEND: " + message, end = Teebo.eol)
		self.sentMessageCount += 1
		self.sock.sendall(bytes(message + Teebo.eol, "utf-8"))
		
	
	def run(self):
		while True:
			self.send()
		
