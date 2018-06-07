import sys
import Teebo


#TODO: PASS support
#TODO: Load settings from json file


##############################################################################
# Links:
##############################################################################
# https://tools.ietf.org/html/rfc1459
# https://tools.ietf.org/html/rfc2812


def main():
	print("=== Teebo starting ===")
	client = Teebo.Client("127.0.0.1", 6667, "Teebo", "#Test")
	
	while True:
		client.run()

	print("Done.")


if __name__ == "__main__":
	main()
