import re
import enum


eol = "\x0D\x0A" # CR LF


def getInfoFromPrefix(prefix):
	# SEE: https://tools.ietf.org/html/rfc2812#section-2.3.1
	data = re.split("^:|!|@", prefix)
	ret = {}
	
	if len(data) > 1:
		ret["nick"] = data[1]
	if len(data) > 2:
		ret["user"] = data[2]
	if len(data) > 3:
		ret["host"] = data[3]
		
	return ret


class HostType(enum.Enum):
	IRC = 0
	TWITCH = 1
	
