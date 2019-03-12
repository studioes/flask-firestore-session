from flask import Flask, request, jsonify, redirect, render_template, session
from flask-firestore-session import Session
from google.cloud import firestore

app = Flask(__name__)

db = firestore.client()

app.secret_key = 'secretkey...'
app.config['SESSION_TYPE'] = 'firestore'
app.config['SESSION_FIRESTORE'] = db
app.config['SESSION_FIRESTORE_COLLECTION'] = 'sessions'
app.config['SESSION_KEY_PREFIX'] = 'mysession_'
app.config['SESSION_USE_SIGNER'] = False
app.config['SESSION_PERMANENT'] = True
app.config['permanent_session_lifetime'] = 60*60*24*30
Session(app)


@app.route('/session_set')
def session_set():
    session['test_key'] = 'test_value'
    return 'Session set.'
    

@app.route('/session_get')
def session_get():
    ret = ''
    for key in session:
        ret += '<p>%s:%s</p>' % (key, session[key])
    return ret


