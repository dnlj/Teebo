import threading
import time
import urllib.request
import json

class PointsThread(threading.Thread):
	def __init__(self):
		super().__init__()
		
		self.pointsTime = time.perf_counter()
		self.pointsInterval = 10
		self.twitch = True
	
	
	def updatePoints(self):
		if (time.perf_counter() - self.pointsTime) < self.pointsInterval:
			return
		
		self.pointsTime = time.perf_counter()
		userList = []
		
		if self.twitch:
			# TODO: http://tmi.twitch.tv/group/user/CHANNEL/chatters
			with urllib.request.urlopen("https://jsonplaceholder.typicode.com/users") as con:
				data = json.loads(con.read())
				
			for user in data:
				name = user.get("name")
				if name is not None:
					userList.append(name)
		else:
			# TODO: For non twitch look into NAMES command
			pass
		
		print("Points done.")
	
	
	def run(self):
		while True:
			self.updatePoints()
			time.sleep((self.pointsInterval + self.pointsTime) - time.perf_counter())
	
