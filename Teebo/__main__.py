import sys
import json
import Teebo
import random


#TODO: PASS support


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


def main():
	print("=== Teebo starting ===")
	
	# Load settings
	with open("settings.json") as settingsFile:
		settings = json.load(settingsFile)
	
	# Create bot
	# TODO: User friendly error reporting for missing field
	client = Teebo.Client(
		settings["host"],
		settings["port"],
		settings["user"],
		settings["channels"]
	)
	
	# Load commands
	client.commandText = {}
	
	for cmd in settings["commands"]:
		client.commandText[cmd["command"]] = cmd["text"]
		client.addCommand(cmd["command"], command_text, "Text command.")
	
	client.addCommand("!roll", command_roll, "Rolls N S sided dice. Ex: !roll 3d6")
	client.addCommand("!help", command_help, "Gets the help text for a command. Ex: !help !roll")
	
	# Create the points thread
	pointsThread = Teebo.PointsThread()
	pointsThread.start()
	
	# Run the bot
	while True:
		client.run()
	
	# Cleanup
	pointsThread.join()
	client.close()
	

if __name__ == "__main__":
	main()
