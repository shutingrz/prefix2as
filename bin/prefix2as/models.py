import ipaddress
import sqlalchemy
from sqlalchemy import asc, desc
from flask import current_app

class Prefix2asModel(object):
	
	def __init__(self):
		pass

	def _initDB(self):
		try:
			from prefix2as import db
			from prefix2as.db.orm.route4 import Route4
		except sqlalchemy.exc.OperationalError as exc:
			current_app.logger.critical("Database connection error: %s" % exc)
			return None, None
		except sqlalchemy.exc.NoSuchTableError as exc:
			current_app.logger.critical("route4 table is not exist. please exec updateRouting.py")
			return None, None
		except sqlalchemy.exc.NoSuchTableError as exc:
			current_app.logger.critical("Unknown OR/M error: %s" % exc)
			raise Exception(exc)

		return db, Route4

	def getRoutes_fromPrefix(self, prefix, date=None):
		db, Route4 = self._initDB()

		if db is Route4 is None:
			return None, 100


		#work around: select all routes without get min size. (if use "order by , very slowly.)
		ip_int = int(ipaddress.ip_address(prefix))
		data =  db.session.query(Route4.asnum, Route4.prefix, Route4.date, Route4.size).\
						 	filter(Route4.start_ip <= ip_int, ip_int <= Route4.end_ip).\
							all()

		#if route is not found.
		if len(data) < 1:
			return None, 110

		#get best path (min size)
		size_tmparray = []
		for i in data:
			size_tmparray.append(i[3])

		min_size = min(size_tmparray)

		routes = []
		for item in data:
			if item[3] == min_size:
				routes.append({'as': item[0], 'prefix': item[1], 'date': item[2]})
			
		return routes, 0

	def getRoutes_fromASnum(self, asnum, date=None):
		db, Route4 = self._initDB()

		if db is Route4 is None:
			return None, 100

		data = db.session.query(Route4.asnum, Route4.prefix, Route4.date, Route4.size).\
					 	filter(Route4.asnum == asnum).\
						all()

		routes = []
		for item in data:
			routes.append({'as': item[0], 'prefix': item[1], 'date': item[2]})

		return routes, 0

