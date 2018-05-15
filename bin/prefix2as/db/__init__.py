from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import scoped_session, mapper
from sqlalchemy.orm.session import sessionmaker
from flask import Flask, current_app

database_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
engine = create_engine(database_uri)

metadata = MetaData(bind=engine)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

class Model(object):
	query = session.query_property()


