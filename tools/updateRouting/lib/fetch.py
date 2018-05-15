import os, re, urllib.request, bz2
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
from logging import getLogger

logger = getLogger(__name__)

class Fetch():
	URL = 1

	SUPPORTED_URLSCHEME = ["http", "https"]

	def __init__(self):
		pass

	def fetch(self, url):
		tmppath = None
		tmppath = self._fetchMRTFile(url)

		if tmppath is None:
			raise NameError("tmppath is None.")
		else:
			return tmppath

	
	def _fetchMRTFile(self, url):
		if not self._isExpectedURLFormat(url):
			raise SyntaxError("url must URL scheme.")

		logger.debug("URL: %s" % url)

		if self._isURLResourceValid(url):
			logger.debug("fetch start.")
			opener = urllib.request.build_opener()
			tmpFilepath, headers = urllib.request.urlretrieve(url)
			logger.debug("fetch end.")
			return tmpFilepath
		else:
			return None

	def _isURLResourceValid(self, url):
		opener = urllib.request.build_opener()

		req = urllib.request.Request(url, method="HEAD")
		resp = opener.open(req)
		return True

	def _isExpectedURLFormat(self, url):
		parse = urlparse(url)
		if parse.scheme in Fetch.SUPPORTED_URLSCHEME:
			return True
		else:
			return False

	def _expandTimeFormat(self, path, time):
		tmppath = path
		while True:
			match = re.search(r"\${(?P<time>%[a-zA-Z])}", tmppath) # ${%m} => %m
			if match:
				datetimeformat = match.group("time")
				strdatetime = time.strftime(datetimeformat)
				tmppath = tmppath.replace("${%s}" % datetimeformat, strdatetime)
			else:
				break

		return tmppath
			

class LocalFetch(Fetch):
	def __init__(self):
		pass

	def fetch(self, url): 
		logger.debug("url: %s" % url)

		url = self._expandTimeFormat(url, datetime.now())

		if self._isFileScheme(url):
			return self._getOSPath(url)

	def _isFileScheme(self, url):
		parse = urlparse(url)
		if parse.scheme == "file":
			return True
		else:
			return False

	def _getOSPath(self, url):
		if not self._isFileScheme(url):
			raise SyntaxError("url is not file scheme")

		parse = urlparse(url)
		return parse.netloc + parse.path


class RouteViewsFetch(Fetch):
	#####
	## Resource: Route Views Project (http://archive.routeviews.org/)
	## frequency of updating: 2 hours
	## timezone: UTC
	## filename format: rib.%Y%m%d.%H00.bz2
	## file format: bz2

	def __init__(self):
		pass

	def fetch(self, url):
		logger.info("RouteViews MRT file fetch start.")
		time = datetime.now(timezone.utc)

		if time.hour % 2 != 0:	# if odd, back an hour
			time -= timedelta(hours=1)

		url = self._expandTimeFormat(url, time)
		mrttmp = self._fetchMRTFile(url)
		mrttmp = self._extractBz2(mrttmp) #extract bz2 data.

		logger.info("...end")
		return mrttmp

	def _extractBz2(self, path):
		f = open(path, "rb")
		bz2Data = f.read()
		f.close()

		extractData = bz2.decompress(bz2Data)
		f = open(path, "wb")
		f.write(extractData)
		f.close()

		return path
