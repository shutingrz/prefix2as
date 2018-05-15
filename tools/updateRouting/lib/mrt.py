import os, sys, subprocess, ipaddress, re
from logging import getLogger

logger = getLogger(__name__)

class MRTController():
	def __init__(self, mrtpath=None, peer_as=None):
		self.mrt = []
		self.bgpdump_path = "bgpdump"

		if mrtpath is not None:
			self.read(mrtpath)

	def setBgpdumpPath(self, bgpdump_path):
		self.bgpdump_path = bgpdump_path

	def read(self, mrtpath, peer_as=None):
		logger.info("MRT data reading...")
		mrt = []
		
		if not os.path.exists(mrtpath):
			raise FileNotFoundError("MRT path '%s' is not found." % mrtpath)

		dumpout = self.bgpdump(mrtpath, self.bgpdump_path)
		dumplines = dumpout.split("\n")
		del dumpout
		logger.debug("MRT data parse start.")
		for dumpline in dumplines:
			route = self._parse(dumpline, peer_as)
			if route is None:
				continue
			else:
			 	mrt.append(route)
		del dumplines
		logger.debug("MRT data parse end. (len=%s)" % len(mrt))

		if len(mrt) > 0:
			self.mrt = mrt

		logger.info("...end")
	
	def export(self):
		if len(self.mrt) > 0:
			return self.mrt
		else:
			raise Exception("MRT has no data.")

	def print_mrt(self):
		for route in self.mrt:
			print(route.items())

	def createSampleData(self):
		mrt = []
		line = "TABLE_DUMP2|1512571800|B|192.168.3.11|65009|1.0.132.0/22|7500 2497 38040 23969|INCOMPLETE|202.249.2.169|0|0||NAG||"
		route = self._parse(line, None)
		mrt.append(route)
		self.mrt = mrt

	def bgpdump(self, mrtpath, bgpdump_path):
		#TABLE_DUMP2|1512571800|B|192.168.3.11|65009|1.0.132.0/22|7500 2497 38040 23969|INCOMPLETE|202.249.2.169|0|0||NAG||
		logger.debug("bgpdump start: %s" % mrtpath)
		try:
			dumpout = subprocess.check_output([bgpdump_path, "-m", mrtpath])
			dumpout = dumpout.decode(encoding="ascii")
		except Exception as e:
			raise Exception("bgpdump: load MRT data exception: %s" % e)
		logger.debug("bgpdump finished.")

		return dumpout
	

	def _parse(self, line, peer_as=None):
		route_arr = line.split("|")

		if len(route_arr) < 14:
			return None

		route = {
#			"type":       route_arr[0], # TABLE_DUMP2
			"date":       route_arr[1], # 1501686000
#			"flag":       route_arr[2], # B
#			"peer_ip":    route_arr[3], # 192.168.2.65
			"peer_as":    route_arr[4], # 65009
			"prefix":     route_arr[5], # 1.0.4.0/22
			"aspath":     route_arr[6], # 59105 2518 4826 38803 56203
#			"origin":     route_arr[7], # IGP
#			"nexthop":    route_arr[8], # 103.48.31.82
#			"localpref":  route_arr[9], # 100
#			"med":        route_arr[10],# 0
#			"comm":       route_arr[11],# *blank
#			"atomic_aggr":route_arr[12],# NAG
#			"merge_aggr" :route_arr[13],# *blank
			"asnum"      :None,
			"start_ip"   :None,
			"end_ip"     :None,
			"size"       :None
		}

		if "::/" in route["prefix"]: #IPv6 is not supported.
			return None
		elif peer_as is not None:
			if route["peer_as"] != peer_as:	# for multi home
				return None

		asnum = route["aspath"].split(" ")[-1]
		
		#asnum is sometimes surrounded by "{}"
		if asnum.isdigit():
			route["asnum"] = asnum
		else:
			match = re.search(r"{(?P<num>\d+)}", asnum)
			if match:
				num = match.group("num")
				if num.isdigit():
					route["asnum"] = num
				else:
				 	return None
			else:
				return None

		#prefix data
		netobj = ipaddress.ip_network(route["prefix"])
		start_ip = int(netobj[0])
		end_ip =   int(netobj[-1])
		size = end_ip - start_ip + 1
		route["start_ip"] = str(start_ip)
		route["end_ip"] = str(end_ip)
		route["size"] = str(size)

		if None in route.values():
			return None
		else:
			return route


	@classmethod
	def bgpdump_dryrun(self, bgpdump_path):
		try:
			dumpout = subprocess.check_output([bgpdump_path, "-T"])
		except Exception as e:
		 	raise NameError("bgpdump is not found. Please set a correct bgpdump path.")
