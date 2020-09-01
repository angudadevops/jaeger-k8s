from typing import List, Dict
from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
from mysql.connector import Error
import json
import requests

from jaeger_client import Config
from flask_opentracing import FlaskTracer
import logging
import time

app = Flask(__name__)

@app.route('/jaeger')
def pull_requests():

  # Fetch a list of pull requests on the opentracing repository
  github_url = "https://api.github.com/repos/opentracing/opentracing-python/pulls"
  r = requests.get(github_url)
  
  json = r.json()
  pull_request_titles = map(lambda item: item['title'], json)
  
  return 'OpenTracing Pull Requests: ' + ', '.join(pull_request_titles)

@app.route('/')
def version():
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'test_db'
    }
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        db_Info = connection.get_server_info()
        cursor.close()
        connection.close()
        return "Connected to MySQL Server {}".format(db_Info)+"<br>"+"If you want to insert users to MySQL, access with /insert"
    except:
        return "Oops!! Unable to Connect to MySQL DB"

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'test_db'
    }
    if request.method == "POST":
        details = request.form
        firstName = details['fname']
        lastName = details['lname']
        connection = mysql.connector.connect(**config)
        cur = connection.cursor()
        cur.execute("INSERT INTO MyUsers(firstname, lastname) VALUES (%s, %s)", (firstName, lastName))
        connection.commit()
        cur.close()
        return redirect(url_for('display_deals'))
    return render_template('index.html')  

'''

@app.route('/')
def index():
    return version()

def dba()-> List[Dict]:
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'test_db'
    }
    try:
        connection = mysql.connector.connect(**config)
        curs = connection.cursor()
        curs.execute("SELECT * FROM MyUsers")
        results = [{firstname: lastname} for (firstname, lastname) in curs]
        curs.close()
        connection.close()
        return results
    except:
        return "Oops!! Unable to Connect to MySQL DB"

@app.route('/db')
def dblist()-> str:
    return json.dumps({'Users are': dba()})

'''

@app.route('/dashboard')       
def display_deals():
    config = {
        'user': 'root',
        'password': 'root',
        'host': 'db',
        'port': '3306',
        'database': 'test_db'
    }
    try:
        connection = mysql.connector.connect(**config)
        curso = connection.cursor()
        curso.execute("SELECT * from MyUsers")
        data = curso.fetchall()
        connection.close()
        #return data
        return render_template("dashboard.html", data=data)

    except Exception as e:
        return (str(e))

"""
Function for Jaeger Opentracing
"""

def initialize_tracer():
    config = Config(
        config={
            'sampler': {'type': 'const', 'param': 1},
            'logging': True,
        },
        service_name='python',
        validate=True,
    )
    return config.initialize_tracer() # also sets opentracing.tracer


flask_tracer = FlaskTracer(initialize_tracer, True, app)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
