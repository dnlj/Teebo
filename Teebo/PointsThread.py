import threading
import time


class PointsThread(threading.Thread):
	def __init__(self, client):
		super().__init__()
		
		self.pointsTime = time.perf_counter()
		self.pointsInterval = 10
		self.client = client
	
	
	def updatePoints(self):
		if (self.pointsInterval + self.pointsTime) - time.perf_counter() > 0:
			return
		
		self.pointsTime = time.perf_counter()
		
		for chan in self.client.channels:
			self.updatePointsForChannel(chan)
	
	
	def updatePointsForChannel(self, channel):
		userList = self.client.getUserListForChannel(channel)
		if not userList: return
		# TODO: points
		
	
	def run(self):
		while True:
			self.updatePoints()
			time.sleep(max((self.pointsInterval + self.pointsTime) - time.perf_counter(), 0))
	
