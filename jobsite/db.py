import datetime
import sqlite3
from flask import current_app, g, flash
from flask.cli import with_appcontext
import click
import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')


def get_db():
  if 'db' not in g: 
    g.db = psycopg2.connect(DATABASE_URL, sslmode='require')
  return g.db

def close_db(e=None):
  db = g.pop('db', None)
  if db is not None:
    db.close()
    
def init_db():
  db = get_db()
  f = current_app.open_resource("sql/initial.sql")
  sql_code = f.read().decode("ascii")
  cur = db.cursor()
  cur.execute(sql_code)
  cur.close()
  db.commit()
  close_db()
   
@click.command('initdb', help="Initialise The Database")
@with_appcontext
def init_db_command():
  init_db()
  click.echo('Database Initialised')

def init_app(app):
  app.teardown_appcontext(close_db)
  app.cli.add_command(init_db_command)
