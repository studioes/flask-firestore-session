# flask-firestore-session
Flask session support Google Cloud Firestore

##JP:
　FlaskのGoogle Cloud Firestoreサポート拡張です。  
　from flask-firestore-session import Session して、app.config['SESSION_TYPE']を'firestore'に、  
app.config['SESSION_FIRESTORE']にFirestoreクライアントを入れた上でSession()すればFlaskのセッションが  
Firestoreに保存されます。  
　Expireは呼び出し時のソフトウェア処理で、キーの寿命は管理されていません。  
　GAE等であれば自動で同じプロジェクトのFirestoreに繋がるのでサンプルのまま動作します。   
　ローカル環境などでは、firestore.client()にサービスアカウントのCredentialを与える必要があります。  


Use:
```
from flask import Flask, session
from flask-firestore-session import Session
from google.cloud import firestore
db = firestore.client()

app.secret_key = 'secret'
app.config['SESSION_TYPE'] = 'firestore'
app.config['SESSION_FIRESTORE'] = db
app.config['SESSION_FIRESTORE_COLLECTION'] = 'seccion'
app.config['SESSION_KEY_PREFIX'] = 'mysession_'
app.config['SESSION_USE_SIGNER'] = False
app.config['SESSION_PERMANENT'] = True
app.config['permanent_session_lifetime'] = 60*60*24*30
Session(app)

@app.route('/session-set')
def session-set():
  session['key'] = 'value'
  return 'Set'
  
@app.route('/session-set')
def session-get():
  value = session['key']
  return 'Value:%s' % (value)
```
