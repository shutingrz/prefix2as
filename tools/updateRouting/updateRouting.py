#!/usr/bin/env python3

import os, sys
from logging import basicConfig, getLogger, DEBUG, INFO
from argparse import ArgumentParser
from configparser import ConfigParser
from lib import mrt, db, fetch

logger = getLogger(__name__)
basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s", level=DEBUG)

def _argparse():
	desc = "usage: %prog [options] mrtpath"
	parser = ArgumentParser(description=desc)
	parser.add_argument("mrtpath", nargs="?")
	parser.add_argument("-v", "--version", help="show version")
	parser.add_argument("-c", "--conf", dest="config", help="config_file path", required=True)
	parser.add_argument("--debug", dest="isDebug", help="print debug strings")
	return parser.parse_args()


def _confparse(conf_file):
	config = ConfigParser()
	config.read(conf_file)

	items =	{	"SYSTEM": [],
	 					"DB": ["dburl"],
						"MRT": ["profile"]
					}
					
	for section in items.keys():
		if section not in config:
			raise NameError("please set [%s] section to config file." % section)
		else:
			for value in items[section]:
				if value not in config[section]:
					raise NameError("please set '%s' value to [%s] section in config file." % (value, section))

	#default settings
	if not "bgpdump_path" in config["SYSTEM"]:
		config["SYSTEM"]["bgpdump_path"] = "bgpdump"
	if not "max_history" in config["SYSTEM"]:
		config["SYSTEM"]["max_history"] = "1"

	profile = config["MRT"]["profile"]
	if not "autodelete" in config[profile]:
		config[profile]["autodelete"] = "0"
	if not "peer_as" in config[profile]:
		config[profile]["peer_as"] = ""
					
	return config


def _fetch(profile):	
	url = None
	mrtfetch = None
	if profile["type"] == "RouteViews":
		url = profile["url"]
		mrtfetch = fetch.RouteViewsFetch()
	elif profile["type"] == "Local":
		url = profile["url"]
		mrtfetch = fetch.LocalFetch()
	else:
		NameError("type %s is not supported." % profile["type"])
	
	if url is None or url == "":
		NameError("url is not set.")

	mrttmp = mrtfetch.fetch(url)
	return mrttmp


def _getMRTData(bgpdump_path, mrtpath, peer_as=None):
	mrtctl = mrt.MRTController()
	mrtctl.setBgpdumpPath(bgpdump_path)

	if peer_as != "":
		mrtctl.read(mrtpath, peer_as)
	else:
		mrtctl.read(mrtpath)

	return mrtctl.export()


def _import(sqlconf, mrtdata, max_history):

	dbctl = db.Route4DBController(sqlconf["dburl"])
	dbctl.update(mrtdata, max_history)

def main():
	args = _argparse()
	config = _confparse(args.config)

	logger.info("updateRouting successfully started.")
	bgpdump_path = config["SYSTEM"]["bgpdump_path"]
	max_history = int(config["SYSTEM"]["max_history"])
	mrttmp = None
	profile = None
	peer_as = None
	autodelete = None

	mrt.MRTController.bgpdump_dryrun(bgpdump_path)

	if args.mrtpath is not None:
		mrttmp = args.mrtpath
	elif config["MRT"]["profile"] != "":
		profileName = config["MRT"]["profile"]
		profile = config[profileName]
		peer_as = profile["peer_as"]
		autodelete = profile["autodelete"]

		mrttmp = _fetch(profile)
	else:
		raise NameError("set mrtpath in commandline arg or profile in config file.")
	
	logger.debug("mrttmp path: %s" % mrttmp)

	mrtdata = _getMRTData(bgpdump_path, mrttmp, peer_as)

	if autodelete == "1":
		try:
			logger.debug("MRT file delete start.")
			os.remove(mrttmp)
			logger.debug("MRT file delete end.")
		except Exception as exc:
			logger.critical("could not delete MRT file: %s" % s)

	sqlconf = config["DB"]
	_import(sqlconf, mrtdata, max_history)

	logger.info("updateRouting all finished!")

if __name__ == "__main__":
	main()
