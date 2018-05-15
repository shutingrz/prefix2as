from flask import Blueprint, jsonify, url_for, current_app, request
from prefix2as.models import Prefix2asModel
import ipaddress

prefix2as = Blueprint('prefix2as', __name__, url_prefix='/prefix2as')

@prefix2as.route('/')
def index():
	return jsonify(
			search = url_for('.search'),
		)

def _makeErrorMessage(code):
	data = {'header': {'status': 'error', 'errorCode': code}, 'response': {}}
	return data

def _makeResponseMessage(response):
	data = {'header': {'status': 'success', 'errorCode': 0}, 'response': response}
	return data

@prefix2as.route('/search', methods=['GET'])
def search():
	ip4 = request.args.get('ip4', None)
	asnum = request.args.get('as', None)

	if ip4 is not None:
		try:
			ipaddress.ip_address(ip4)
		except Exception as exp:
			return jsonify(_makeErrorMessage(10))
		model = Prefix2asModel()
		routes, code = model.getRoutes_fromPrefix(ip4)
	elif asnum is not None:
		if asnum.isdigit():
			if int(asnum) < 2**32:
				model = Prefix2asModel()
				routes, code = model.getRoutes_fromASnum(asnum)
			else:
				return jsonify(_makeErrorMessage(20))
		else:
			return jsonify(_makeErrorMessage(30))
	else:
		return jsonify(_makeErrorMessage(40))
	
	if routes is None:
		return jsonify(_makeErrorMessage(code))
	else:
		return jsonify(_makeResponseMessage(routes))


