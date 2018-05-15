#!/usr/bin/env python3

from flask import Flask, Blueprint
from prefix2as.views import prefix2as

def create_app():

	app = Flask(__name__)
	try:
		app.config.from_pyfile('../prefix2as.conf')
	except FileNotFoundError as exc:
		app.logger.critical("'../prefix2as.conf' is not found.")
		raise FileNotFoundError(exc)

	try:
		dburl = app.config['DBURL']
		app.config['SQLALCHEMY_DATABASE_URI'] = dburl
		app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
	except KeyError as exc:
		app.logger.critical("DBURL is not set. please set dburl at prefix2as.conf!")
		raise KeyError(exc)
	

	app.register_blueprint(prefix2as)

	return app

if __name__ == '__main__':
	app = create_app()
	app.run(debug=True, host=app.config['LISTEN'], port=app.config['PORT'])
