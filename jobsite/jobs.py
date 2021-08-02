import datetime
from flask import render_template, request, redirect, url_for, jsonify, Flask, g, Blueprint, flash
from . import db
from flask import Flask, render_template, request
import sys
import bs4
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import psycopg2
import os

bp = Blueprint("jobs", "jobs", url_prefix="")

@bp.route("/")
def dashboard():
  return render_template("login.html", url_prefix="")


@bp.route("/login", methods = ["GET", "POST"])
def login():
  conn = db.get_db()
  cursor = conn.cursor()
  status = None
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    cursor.execute("select pass from users where name = %s;", (username,))
    lpass = cursor.fetchone()
    if lpass[0] != password:
      status = "Incorrect User Details, Try Again"
    else:
      cursor.execute("select id from users where name = %s;", (username,))
      owner = cursor.fetchone()
      oid = owner[0]
      return redirect(url_for("jobs.home", oid=oid), 302)
  return render_template("login.html", status=status)
  

@bp.route("/create")
def create():
  return render_template("create.html")
  

@bp.route("/createuser", methods=["POST"])
def createuser():
  conn = db.get_db()
  cursor = conn.cursor()
  username = request.form['username']
  password = request.form['password']
  
  cursor.execute(f"select name from users where name = %s;", (username,))
  cname = cursor.fetchone()
  if cname is not None:
    flash('Username already exists')
    return redirect(url_for("jobs.create"), 302)
  cursor.execute("""insert into users (name, pass) values (%s, %s);""", (username, password))
  conn.commit()
  return redirect(url_for("jobs.dashboard"), 302)
  

@bp.route("/home/<oid>")
def home(oid):
  oid = oid
  oby = ["id", "name", "found"]
  conn = db.get_db()
  cursor = conn.cursor()
  
  d = datetime.datetime.now().strftime("%Y-%m-%d")
  cursor.execute("""
  delete from jobs
  where (%s-fdate) >= 7 and oid = %s""",(d,oid))
  
  oid = oid
  if oby[0] == request.args.get("order_by", "id"):
    order = request.args.get("order", "asc")
    if order == "asc":
      cursor.execute(f"select id, name, company, fdate, url from jobs where oid = %s order by id", (oid,))
    else:
      cursor.execute(f"select id, name, company, fdate, url from jobs where oid = %s order by id desc", (oid,))
  elif oby[1] == request.args.get("order_by", "name"):
    order = request.args.get("order", "asc")
    if order == "asc":
      cursor.execute(f"select id, name, company, fdate, url from jobs where oid = %s order by name", (oid,))
    else:
      cursor.execute(f"select id, name, company, fdate, url from jobs where oid = %s order by name desc", (oid,))
  elif oby[2] == request.args.get("order_by", "created"):
    order = request.args.get("order", "asc")
    if order == "asc":
      cursor.execute(f"select id, name, company, fdate, url from jobs where oid = %s order by fdate", (oid,))
    else:
      cursor.execute(f"select id, name, company, fdate, url from jobs where oid = %s order by fdate desc", (oid,))
  jobs = cursor.fetchall()
  conn.commit()
  return render_template("home.html", oid=oid, jobs=jobs, order="desc" if order=="asc" else "asc")
  
  
@bp.route("/find/<oid>")
def find(oid):
  oid = oid
  return render_template("findjobs.html", oid=oid)
  

@bp.route("/findjobs/<oid>", methods=["POST"])
def findjobs(oid):
  oid = oid
  conn = db.get_db()
  cursor = conn.cursor()
  l = []
  
  jobname = request.form['jobname']
  location = request.form['location']
  d = datetime.datetime.now().strftime("%Y-%m-%d")
   
  driver = webdriver.Firefox(options=FF_options, firefox_profile=FF_profile, executable_path=os.environ.get("GECKODRIVER_PATH"), firefox_binary=FirefoxBinary(os.environ.get("FIREFOX_BIN")))
  
  l = jobname.split()
  url = "https://www.naukri.com/"+l[0]+"-"+l[1]+"-jobs-in-"+location+"?k="+l[0]+"%20"+l[1]+"&l="+location
  driver.get(url)
  soup = bs4.BeautifulSoup(driver.page_source, features = "html.parser")
  driver.close()
  
  results = soup.find(class_='list')
  job = results.find_all('article', class_='jobTuple bgWhite br4 mb-8')
  
  for i in job:
    
    job_titles = i.find('a', class_='title fw500 ellipsis')
    company = i.find('div', class_='mt-7 companyInfo subheading lh16')
    company_name = company.find('a', class_='subTitle ellipsis fleft')
    job_name = (job_titles.text)
    companyname = (company_name.text)
    joburl = (job_titles.get('href'))
    
    cursor.execute("""insert into jobs (name, company, oid, fdate, url) values (%s, %s, %s, %s, %s);""", (job_name, companyname, oid, d, joburl))
    conn.commit()
    
  return redirect(url_for("jobs.home", oid=oid), 302)
  

@bp.route("/refresh/<oid>")
def delete(oid):
  oid = oid
  conn = db.get_db()
  cursor = conn.cursor()
  cursor.execute("""
  delete from jobs
  where oid = %s;""",(oid,))
  conn.commit()
  return redirect(url_for("jobs.find", oid=oid), 302)
    
