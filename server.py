import api_communicator
from utils import eprint
import os
import pymongo
import hashlib
import binascii

from flask import Flask, send_from_directory, jsonify, request
app = Flask(__name__, static_folder='views')

import json

@app.route("/")
def hello():
  return app.send_static_file('index.html')

@app.route('/<path:path>')
def send_static(path):
  return send_from_directory('public', path)

@app.route('/register', methods=["GET"])
def view_register_page():
  eprint('hello')
  return app.send_static_file('register.html')
  
@app.route('/registration_successful', methods=["GET"])
def registration_successful():
  return app.send_static_file('registration_successful.html')
  
@app.route('/myhome', methods=["GET"])
def homepage():
  return app.send_static_file('myhome.html')

@app.route('/register', methods=["POST"])
def register():
  db = get_mongo_db()
  accounts = db['accounts']
  if len(list(accounts.find({'subdomain': request.form['subdomain']}))) != 0:
    return jsonify({'error': 'Account Already Exists'}), 403
  working_token = api_communicator.test_token(request.form['subdomain'], request.form['token'])
  if working_token:
    secret_salt = os.environ['SECRET_SALT']
    accounts.insert({'subdomain': request.form['subdomain'],
                     'kiln_token': request.form['token'],
                     'hyper_token': binascii.hexlify(os.urandom(16)),
                     'kiln_users': [],
                     'password': hashlib.sha256(request.form['password'] + secret_salt).hexdigest()})
    return "'OK'"
  else:
    return jsonify({'error': 'Bad Token'}), 403

@app.route('/login', methods=["POST"])
def login():
  db = get_mongo_db()
  accounts = db['accounts']
  matching_accounts = list(accounts.find({'subdomain': request.form['subdomain']}))
  saved_pw = matching_accounts[0]['password']
  secret_salt = os.environ['SECRET_SALT']
  if hashlib.sha256(request.form['password'] + secret_salt).hexdigest() != saved_pw:
    return jsonify({'error': 'Unauthorized'}), 401
  return matching_accounts[0]['hyper_token']
  
@app.route('/users', methods=["POST"])
def add_user():
  db = get_mongo_db()
  eprint('trying to update')
  eprint(db['accounts'].update({'hyper_token': request.cookies['hyper-token']}, {'$push': {'kiln_users': {'username': request.args['user'], 'ixUser': request.args['ixuser']}}}))
  eprint('updated')
  return "'OK'"
  
@app.route('/users', methods=["GET"])
def get_users():
  hyper_token = request.cookies["hyper-token"]
  eprint('hyper_token: ' + hyper_token)
  db = get_mongo_db()
  user_list = db['accounts'].find({'hyper_token': hyper_token})[0]['kiln_users']

  return jsonify({'users' : user_list })
  

def get_mongo_db():
  mongo_uri = 'mongodb://' + os.environ['MONGO_USER'] + ':' + os.environ['MONGO_PASSWORD'] + '@' + os.environ['MONGO_HOST'] + ":" + os.environ['MONGO_PORT'] + '/' + os.environ['MONGO_DB_NAME']
  return pymongo.MongoClient(mongo_uri).get_default_database()
  

@app.route('/hook-target', methods=["POST"])
def handle_kiln_hook():
  payload = json.loads(request.form['payload'])
  url = payload['repository']['url']
  subdomain = url[url.find('://') + 3 : url.find('.kilnhg')]
  db = get_mongo_db()
  account = db['accounts'].find({'subdomain': subdomain})[0]
  users = account['kiln_users']
  token = account['kiln_token']
  api_communicator.process_hook(payload, subdomain, users, token)
  return "'OK'"
  
if __name__ == "__main__":
  # Remember to specify both host and port because HyperDev expects them
  app.debug = True
  app.run(host='0.0.0.0', port=3000, threaded=True)