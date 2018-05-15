import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, DateTime, text, DATETIME, BIGINT, INTEGER
#from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base
from logging import getLogger
from datetime import datetime

Base = declarative_base()

logger = getLogger(__name__)

class DBController():
	def __init__(self, dburl):
		self.dburl = dburl
		self.engine = None
		self.Session = None

	def getSession(self):
		return self._createSession(self.dburl)

	def _createSession(self, dburl):
		engine = create_engine(dburl)
		Base.metadata.create_all(bind=engine)
		Session = sessionmaker(bind=engine)
		return Session()

		
class Route4DBController(DBController):
	def __init__(self, dburl):
		super(Route4DBController, self).__init__(dburl)

	def update(self, mrt, max_history):
		logger.info("Database updating...")
		session = self.getSession()

		self._deleteHistory(session, max_history)

		histid = self._createHistory(session)

		logger.debug("insert statement create start.")
		route4 = [dict(history_id=histid,
									date=route["date"],
									asnum=route["asnum"],
									prefix=route["prefix"],
									start_ip=route["start_ip"],
									end_ip=route["end_ip"],
									size=route["size"]
							) for route in mrt]
		session.execute(Route4.__table__.insert(), route4)
		logger.debug("insert statement create end.")
		logger.debug("commit start.")
		session.commit()
		logger.debug("commit end.")
		session.close()

		logger.info("...end")

	def _deleteHistory(self, session, max_history):
		if max_history == 0: # no delete.
			return False

		res = session.query(Route4History.id).order_by(Route4History.id.desc()).first()

		#for initial commit.
		if res is None:
			logger.debug("_deleteHistory: did not delete (history is none.)")
			return False

		deletable_maxid = int(res.id) - max_history + 1

		logger.debug("max_history:%s , deletable_maxid:%s" % (max_history, deletable_maxid))

		if deletable_maxid < 1:
			logger.debug("_deleteHistory: did not delete (deletable_maxid < 1)")
			return False

		logger.debug("Route4 delete: id <= %s start." % deletable_maxid)
		session.query(Route4).filter(Route4.history_id <= deletable_maxid).delete()
		session.commit()
		logger.debug("Route4 deleted.")
		return True

	def _createHistory(self, session):
		history = Route4History()
		session.add(history)
		session.commit()

		res = session.query(Route4History.id).order_by(Route4History.id.desc()).first()
		return res.id


class Route4(Base):
	__tablename__ = "route4"
	
	id = Column(BIGINT, primary_key=True, autoincrement=True)
	history_id = Column(INTEGER)
	date = Column(BIGINT)
	asnum = Column(BIGINT)
	prefix = Column(String(18)) # max: 255.255.255.255/32 => 18
	start_ip = Column(BIGINT)
	end_ip = Column(BIGINT)
	size = Column(INTEGER)

class Route4History(Base):
	__tablename__ = "route4history"

	id = Column(BIGINT, primary_key=True, autoincrement=True)
	created_at = Column(DATETIME, default=datetime.now)

		








