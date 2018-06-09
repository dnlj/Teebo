import sys
import json
import Teebo


#TODO: PASS support


##############################################################################
# Links:
##############################################################################
# https://tools.ietf.org/html/rfc1459
# https://tools.ietf.org/html/rfc2812


def command_text(client, channel, user, cmd, cmdArgs):
	text = client.commandText.get(cmd)
	
	if text is not None:
		client.send(
			"PRIVMSG "
			+ channel
			+ " :"
			+ text
		)
		

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
	
	# Run the bot
	while True:
		client.run()
	
	# Cleanup
	client.close()
	

if __name__ == "__main__":
	main()
