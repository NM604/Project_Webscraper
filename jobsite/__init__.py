import os
from flask import Flask, render_template, flash
import psycopg2
from . import db

def create_app(test_config=None):
  app = Flask("jobsite")
  app.secret_key = 'very_secret_key'
  app.config.from_mapping(DATABASE="jobsite")
  if test_config is not None:
    app.config.update(test_config)
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass
  
  from . import jobs
  app.register_blueprint(jobs.bp)
  
  from . import db
  db.init_app(app)
  
  return app
