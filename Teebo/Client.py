import socket
import Teebo
import shlex
import traceback
import time
import urllib.request
import json


class Client:
	def __init__(self, settings):
		self.data = ""
		self.registered = False
		self.processors = {}
		self.commands = {}
		self.maxMessagesPerSecond = 20
		self.sentMessageCount = 0
		self.messageTime = time.perf_counter()
		self.hostType = Teebo.HostType[settings["type"].upper()]
		
		# Create our connection
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((settings["host"], settings["port"]))
		
		# Setup processors
		self.setMessageProcessors("PING", Client.__messageProcessor_PING)
		self.setMessageProcessors("001", Client.__messageProcessor_RPL_WELCOME)
		self.setMessageProcessors("PRIVMSG", Client.__messageProcessor_PRIVMSG)
		self.setMessageProcessors("353", Client.__messageProcessor_RPL_NAMES)
		self.setMessageProcessors("366", Client.__messageProcessor_RPL_ENDOFNAMES)
		
		# Points thread
		self.pointsThread = Teebo.PointsThread(self, settings["pointAmount"], settings["pointInterval"])
		self.pointsThread.start()
		
		# Receiver thread
		self.receiverThread = Teebo.ReceiverThread(self.sock)
		self.receiverThread.start()
		
		# Send thread
		self.sendThread = Teebo.SendThread(self.sock)
		self.sendThread.start()
		
		# Register
		nickname = settings["user"]
		password = settings["pass"]
		self.channels = settings["channels"]
		if password: self.send("PASS " + password)
		self.send("USER " + nickname + " 0 * :" + nickname + "_real")
		self.send("NICK " + nickname)
		
	
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
		
	
	def __messageProcessor_RPL_WELCOME(self, message):
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
			user = Teebo.getInfoFromPrefix(message.prefix)["nick"]
			resp = cmdData["func"](self, channel, user, cmd, data)
		
		# Send a response
		if resp:
			self.send("PRIVMSG " + channel + " :" + str(resp))
			
	
	def __messageProcessor_RPL_NAMES(self, message):
		pass
		
	
	def __messageProcessor_RPL_ENDOFNAMES(self, message):
		pass
	
	
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
		
		if self.hostType == Teebo.HostType.IRC:
			# TODO: Normal IRC support. Look into NAMES command.
			pass
		elif self.hostType == Teebo.HostType.TWITCH:
			with urllib.request.urlopen("http://tmi.twitch.tv/group/user/" + channel[1:] + "/chatters") as con:
				data = json.loads(con.read())["chatters"]
			
			for user in data["moderators"]: userList.append(user)
			for user in data["staff"]: userList.append(user)
			for user in data["admins"]: userList.append(user)
			for user in data["global_mods"]: userList.append(user)
			for user in data["viewers"]: userList.append(user)
		
		return userList
		
	
	def run(self):
		while True:
			self.process(self.receiverThread.queue.get())
			
	
	def send(self, message):
		self.sendThread.queue.put(message)


	def setMessageProcessors(self, command, func):
		self.processors[command] = func

	
	def process(self, message):
		Teebo.log("RECV: " + str(message), end = Teebo.eol)
		
		# Handle the command
		func = self.processors.get(message.command)
		if func is not None:
			try:
				func(self, message)
			except:
				Teebo.log("ERROR: Exception thrown in the function for command: " + message.command)
				traceback.print_exc()
				
