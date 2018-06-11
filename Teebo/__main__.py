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
			total = 0
			
			for _ in range(0, count):
				total += random.randint(1, sides)
				
			return "@" + user + " - " + str(total)

	return "@" + user + " - Invalid input for command \"" + cmd + "\""


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
		client.addCommand(cmd["command"], command_text)
	
	client.addCommand("!roll", command_roll)
	
	# Run the bot
	while True:
		client.run()
	
	# Cleanup
	client.close()
	

if __name__ == "__main__":
	main()
