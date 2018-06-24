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
		self.channelIds = {}
		self.databaseInit()
		
	
	def databaseInit(self):
		with sqlite3.connect(self.dbfile) as con:
			with closing(con.cursor()) as cur:
				cur.execute('''
					CREATE TABLE IF NOT EXISTS channels (
						id INTEGER PRIMARY KEY NOT NULL,
						channel TEXT UNIQUE NOT NULL
					)
				''')
				
				for chan in self.client.channels:
					self.setupChannel(cur, chan)
	
	
	def setupChannel(self, cursor, channel):
		channel = channel.lower()
		
		cursor.execute('''INSERT OR IGNORE INTO channels (channel) VALUES (:channel)''', {
			"channel": channel,
		})
		
		cursor.execute('''SELECT id FROM channels WHERE channel = :channel''', {
			"channel": channel,
		})
		
		self.channelIds[channel] = str(cursor.fetchone()[0])
		
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS users_''' + self.channelIds[channel] + ''' (
				id INTEGER PRIMARY KEY NOT NULL,
				username TEXT UNIQUE NOT NULL,
				points INTEGER NOT NULL DEFAULT 0
			)
		''')
	
	
	def addPoints(self, channel, user, amount):
		user = user.lower()
		channel = channel.lower()
		
		with sqlite3.connect(self.dbfile) as con:
			with closing(con.cursor()) as cur:
				cur.execute('''UPDATE users_''' + self.channelIds[channel] + ''' SET points = points + :amount WHERE username = :user''', {
					"user": user,
					"amount": amount,
				})

				if cur.rowcount < 1:
					cur.execute('''INSERT INTO users_''' + self.channelIds[channel] + ''' (username, points) VALUES (:user, :amount)''', {
						"user": user,
						"amount": amount,
					})
	
	
	def getPoints(self, channel, user):
		user = user.lower()
		channel = channel.lower()
		
		with sqlite3.connect(self.dbfile) as con:
			with closing(con.cursor()) as cur:
				cur.execute('''SELECT points FROM users_''' + self.channelIds[channel] + ''' WHERE username = :user''', {
					"user": user,
				})
				
				points = cur.fetchone()
				
				if points is None:
					return 0
				else:
					return points[0]
	
	
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
					self.addPoints(channel, user, self.pointAmount)
	
	
	def run(self):
		while True:
			self.updatePoints()
			time.sleep(max((self.pointInterval + self.pointTime) - time.perf_counter(), 0))
	
