import socket
import Teebo
import shlex
import traceback
import time
import urllib.request
import json


class Client:
	eol = "\x0D\x0A" # CR LF
	
	
	def __init__(self, ip, port, nickname, password, channels):
		self.data = ""
		self.registered = False
		self.processors = {}
		self.commands = {}
		self.maxMessagesPerSecond = 20
		self.sentMessageCount = 0
		self.messageTime = time.perf_counter()
		self.twitch = True
		
		# Create our connection
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((ip, port))
		
		if password: self.send("PASS " + password)
		self.send("USER " + nickname + " 0 * :" + nickname + "_real")
		self.send("NICK " + nickname)
		
		self.channels = channels
		
		# Setup processors
		self.setMessageProcessors("PING", Client.__messageProcessor_PING)
		self.setMessageProcessors("MODE", Client.__messageProcessor_MODE)
		self.setMessageProcessors("PRIVMSG", Client.__messageProcessor_PRIVMSG)
		
		# Points thread
		self.pointsThread = Teebo.PointsThread(self)
		self.pointsThread.start()
		
	
	def __enter__(self):
		return self
		
	
	def __exit__(self, exc_type, exc_value, traceback):
		self.close()
		
	
	def close(self):
		self.sock.shutdown(socket.SHUT_RDWR)
		self.sock.close()
		self.pointsThread.join()
	
	def __messageProcessor_PING(self, message):
		self.send("PONG :" + message.trailing)
		
	
	def __messageProcessor_MODE(self, message):
		if not self.registered:
			self.onRegistered()
			self.registered = True
			
	
	def __messageProcessor_PRIVMSG(self, message):
		data = shlex.split(message.trailing)
		cmd = data.pop(0)
		cmdData = self.commands.get(cmd)
		resp = None
		
		# Run the command if it exists
		if cmdData is not None:
			channel = message.params[0]
			user = message.prefix[1:]
			resp = cmdData["func"](self, channel, user, cmd, data)
		
		# Send a response
		if resp:
			self.send("PRIVMSG " + channel + " :" + str(resp))
	
	def onRegistered(self):
		for channel in self.channels:
			self.send("JOIN " + channel)
		
	
	def addCommand(self, cmd, func, helpText):
		self.commands[cmd] = {
			"func": func,
			"help": helpText
		}
		
	
	def getUserListForChannel(self, channel):
		userList = []
		
		if self.twitch:
			with urllib.request.urlopen("http://tmi.twitch.tv/group/user/" + channel[1:] + "/chatters") as con:
				data = json.loads(con.read())["chatters"]
			
			for user in data["moderators"]: userList.append(user)
			for user in data["staff"]: userList.append(user)
			for user in data["admins"]: userList.append(user)
			for user in data["global_mods"]: userList.append(user)
			for user in data["viewers"]: userList.append(user)
		else:
			# TODO: Normal IRC support. Look into NAMES command.
			pass
		
		return userList
		
	
	def run(self):
		# Split into messages
		self.data += self.sock.recv(1024).decode("utf-8")
		messages = self.data.split(self.eol)

		# Handler partial messages
		self.data = messages.pop()

		# Process messages
		for message in messages:
			self.process(Teebo.Message(message))
			
	
	def updateMessageTime(self):
		curTime = time.perf_counter()
		if (curTime - self.messageTime) >= 1.0:
			self.messageTime = curTime
			self.sentMessageCount = 0
	
	
	def send(self, message):
		# Wait until we can send a message
		self.updateMessageTime()
		
		while self.sentMessageCount >= self.maxMessagesPerSecond:
			time.sleep((1 + self.messageTime) - time.perf_counter())
			self.updateMessageTime()
		
		print("SEND: " + message, end = self.eol)
		self.sentMessageCount += 1
		self.sock.send(bytes(message + self.eol, "utf-8"))


	def setMessageProcessors(self, command, func):
		self.processors[command] = func

	
	def process(self, message):
		print("RECV: " + str(message), end = self.eol)
		
		# Handle the command
		func = self.processors.get(message.command)
		if func is not None:
			try:
				func(self, message)
			except:
				print("ERROR: Exception thrown in the function for command: " + message.command)
				traceback.print_exc()
				
