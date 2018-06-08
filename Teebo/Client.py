import socket
import Teebo


class Client:
	eol = "\x0D\x0A" # CR LF

	def __init__(self, ip, port, nickname, channel):
		self.data = ""
		self.registered = False
		self.processors = {}

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((ip, port))
		self.send("USER " + nickname + " 0 * :" + nickname + "_real")
		self.send("NICK " + nickname)
		self.channel = channel
		
		self.setMessageProcessors("PING", Client.__messageProcessor_PING)
		self.setMessageProcessors("MODE", Client.__messageProcessor_MODE)
		
	
	def __messageProcessor_PING(self, message):
		self.send("PONG :" + message.trailing)
		
	
	def __messageProcessor_MODE(self, message):
		if not self.registered:
			self.onRegistered()
			self.registered = True
		
	
	def onRegistered(self):
		self.send("JOIN " + self.channel)
		del self.channel
		
	
	def run(self):
		# Split into messages
		self.data += self.sock.recv(1024).decode("utf-8")
		messages = self.data.split(self.eol)

		# Handler partial messages
		self.data = messages.pop()

		# Process messages
		for message in messages:
			self.process(Teebo.Message(message))
			
	
	def send(self, message):
		print("SEND: " + message, end = self.eol)
		self.sock.send(bytes(message + self.eol, "utf-8"))


	def setMessageProcessors(self, command, func):
		self.processors[command] = func

	
	def process(self, message):
		print("RECV: " + str(message), end = self.eol)

		func = self.processors.get(message.command)
		if func is not None:
			func(self, message)

