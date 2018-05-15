from prefix2as import db

class Route4(db.Model):
	def __init__(self, id, history_id, date, asnum, prefix, start_ip, end_ip, size):
		self.id = id
		self.history_id = history_id
		self.asnum = asnum
		self.prefix = prefix
		self.start_ip = start_ip
		self.end_ip = end_ip
		self.size = size

db.mapper(Route4, db.Table('route4', db.metadata, autoload=True))

