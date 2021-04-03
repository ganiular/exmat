import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
	if 'db' not in g:
		g.db = sqlite3.connect(
			current_app.config["DATABASE"],
			detect_types=sqlite3.PARSE_DECLTYPES 
			# it convert each culumn to his suitable type
		)
		g.db.row_factory = sqlite3.Row
		
	return g.db

def close_db(e=None):
	db = g.pop('db', None)
	
	if db is not None:
		db.close()
		
def init_db():
	db = get_db()
	
	with current_app.open_instance_resource('schema.sql') as f:
		db.executescript(f.read().decode("utf-8"))

@click.command('init-db')
@with_appcontext
def init_db_command():
	"command line interface call of 'init-db' to execute this block"
	init_db()
	click.echo("Database Intitialized")

def register_with(app):
	app.teardown_appcontext(close_db) # close_db is run after every response
	app.cli.add_command(init_db_command) # add cmd line interface to flask
