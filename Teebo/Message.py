class Message:
	def __init__(self, message):
		self.prefix = ""
		self.command = ""
		self.params = []
		self.trailing = ""

		if message:
			self.populate(message)
			
	
	def __str__(self):
		return " ".join(
			filter(None, [
				self.prefix,
				self.command,
				" ".join(self.params),
				":" + self.trailing,
			])
		)

	
	def populate(self, message):
		trailPos = message.find(" :")
		
		if trailPos > -1:
			self.trailing = message[trailPos + 2:]

		data = message[:trailPos].split()

		if message[0] == ":":
			self.prefix = data.pop(0)
		
		if len(data) > 0:
			self.command = data.pop(0)
		
		self.params = data
