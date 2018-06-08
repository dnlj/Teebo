import sys
import json
import Teebo


#TODO: PASS support


##############################################################################
# Links:
##############################################################################
# https://tools.ietf.org/html/rfc1459
# https://tools.ietf.org/html/rfc2812

def messageProcessor_PING(client, message):
	client.send("PONG :" + message.trailing)


def messageProcessor_MODE(client, message):
	client.onRegistered()


def main():
	print("=== Teebo starting ===")

	with open("settings.json") as settingsFile:
		settings = json.load(settingsFile)

		# TODO: User friendly error reporting for missing field
		client = Teebo.Client(
			settings["host"],
			settings["port"],
			settings["user"],
			settings["channel"]
		)
	
	client.setMessageProcessors("PING", messageProcessor_PING)
	client.setMessageProcessors("MODE", messageProcessor_MODE)

	while True:
		client.run()

	print("Done.")


if __name__ == "__main__":
	main()
