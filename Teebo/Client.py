import socket
import Teebo


class Client:
	eol = "\x0D\x0A" # CR LF

	def __init__(self, ip, port, nickname, channel):
		self.data = ""

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((ip, port))
		self.send("USER " + nickname + " 0 * :" + nickname + "_real")
		self.send("NICK " + nickname)
		self.send("JOIN " + channel)

	
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
		
	
	def process(self, message):
		if message.command == "PING":
			self.send("PONG :" + message.trailing)

		print("RECV: " + str(message), end = self.eol)
