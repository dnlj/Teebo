import sys
import json
import Teebo
import random
import threading


##############################################################################
# Links:
##############################################################################
# https://tools.ietf.org/html/rfc1459
# https://tools.ietf.org/html/rfc2812


def command_text(client, channel, user, cmd, args):
	return client.commandText.get(cmd)


def command_roll(client, channel, user, cmd, args):
	if not args:
		return
	
	parts = args[0].split("d")
	
	if len(parts) == 2:
		count = parts[0]
		sides = parts[1]
		
		if count.isdigit() and sides.isdigit():
			count = int(count)
			sides = int(sides)
			
			if count <= 100 and sides <= 1000:
				total = 0
				
				for _ in range(0, count):
					total += random.randint(1, sides)
				
				return "@" + user + " - " + str(total)

	return "@" + user + " - Invalid input for command \"" + cmd + "\""


def command_help(client, channel, user, cmd, args):
	if len(args) != 1: return
	
	cmdData = client.commands.get(args[0])
	if cmdData is not None:
		return args[0] + " - " +cmdData["help"]


class Command_Lottery:
	def __init__(self, client):
		self.client = client
		self.channels = {}
		self.duration = 10
		self.minUsers = 2
		
		# TODO: Add cooldown between?
		
		for chan in client.channels:
			self.resetLottery(chan)
	
	
	def resetLottery(self, channel):
		self.channels[channel] = {
			"users": [],
			"weights": [],
			"thread": threading.Timer(self.duration, self.doLottery, [channel]),
			"pot": 0,
		}
	
	
	def doLottery(self, *args, **kwargs):
		chan = args[0]
		chanData = self.channels[chan]
		
		if len(set(chanData["users"])) < self.minUsers:
			self.client.send("PRIVMSG " + chan + " :The lottery has been canceled. There must be at least " + str(self.minUsers) + " players.")
			# TODO: Give users back points
			return
		
		winner = random.choices(
			chanData["users"],
			chanData["weights"]
		)[0]
		
		pot = chanData["pot"]
		self.client.send("PRIVMSG " + chan + " :Congratulations to @" + winner + " for winning " + str(pot) + " in the lottery!")
		self.client.pointsThread.addPoints(chan, winner, pot)
		
		self.resetLottery(chan)
	
	
	def __call__(self, client, channel, user, cmd, args):
		if len(args) < 1: return
		
		count = args[0]
		if count.isdigit():
			count = int(count)
			chanData = self.channels[channel]
			
			if client.pointsThread.checkAndRemovePoints(channel, user, count):
				chanData["users"].append(user)
				chanData["weights"].append(count)
				chanData["pot"] += count
				
				if not chanData["thread"].is_alive():
					client.send("PRIVMSG " + channel + " :A new lottery has begun. Type !lottery {amount} to enter.")
					chanData["thread"].start()
				
				return "@" + user + " has purchased " + str(count) + " tickets. Current pot is " + str(chanData["pot"])
			else:
				return "@" + user + " - Insufficient points"
		
		return "@" + user + " - Invalid input for command \"" + cmd + "\""


def main():
	Teebo.log("=== Teebo starting ===")
	
	# Load settings
	with open("./settings.json") as settingsFile:
		settings = json.load(settingsFile)
	
	# Create bot
	# TODO: User friendly error reporting for missing field
	client = Teebo.Client(settings)
	
	# Load commands
	client.commandText = {}
	
	for cmd in settings["commands"]:
		client.commandText[cmd["command"]] = cmd["text"]
		client.addCommand(cmd["command"], command_text, "Text command.")
	
	client.addCommand("!roll", command_roll, "Rolls N S sided dice. Ex: !roll 3d6")
	client.addCommand("!help", command_help, "Gets the help text for a command. Ex: !help !roll")
	client.addCommand("!lottery", Command_Lottery(client), "TODO: add help text")
	
	# Run the bot
	client.run()
	
	# Cleanup
	client.close()
	

if __name__ == "__main__":
	main()
