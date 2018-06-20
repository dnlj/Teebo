import threading
import time
import sqlite3
from contextlib import closing


class PointsThread(threading.Thread):
	def __init__(self, client, pointAmount, pointInterval):
		super().__init__()
		
		self.pointTime = time.perf_counter()
		self.pointInterval = pointInterval
		self.pointAmount = pointAmount
		self.client = client
		self.dbfile = "userdata.db"
		self.databaseInit()
		
	
	def databaseInit(self):
		with sqlite3.connect(self.dbfile) as con:
			with closing(con.cursor()) as cur:
				cur.execute('''
					CREATE TABLE IF NOT EXISTS users (
						id INTEGER PRIMARY KEY NOT NULL,
						username TEXT UNIQUE NOT NULL,
						points INTEGER NOT NULL DEFAULT 0
					)
				''')
		
	
	def updatePoints(self):
		if (self.pointInterval + self.pointTime) - time.perf_counter() > 0:
			return
		
		self.pointTime = time.perf_counter()
		
		# TODO: Should use a new DB or table for each channel?
		for chan in self.client.channels:
			self.updatePointsForChannel(chan)
	
	
	def updatePointsForChannel(self, channel):
		userList = self.client.getUserListForChannel(channel)
		
		if not userList: return
		
		with sqlite3.connect(self.dbfile) as con:
			with closing(con.cursor()) as cur:
				for user in userList:
					cur.execute("UPDATE users SET points = points + :amount WHERE username = :user", {
						"user": user,
						"amount": self.pointAmount,
					})
					
					if cur.rowcount < 1:
						cur.execute("INSERT INTO users (username, points) VALUES (:user, :amount)", {
							"user": user,
							"amount": self.pointAmount,
						})
					
	
	def run(self):
		while True:
			self.updatePoints()
			time.sleep(max((self.pointInterval + self.pointTime) - time.perf_counter(), 0))
	
