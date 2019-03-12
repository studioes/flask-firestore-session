# flask-firestore-session
Flask session support Google Cloud Firestore

## JP:  
　FlaskのGoogle Cloud Firestoreサポート拡張です。  
　from flask-firestore-session import Session して、app.config['SESSION_TYPE']を'firestore'にした上でSession(app)すれば  
 FlaskのセッションがFirestoreに保存されます。  
　app.confug['SESSION_FIRESTORE']に独自で建てたFirestore.clientを入れることが可能です（GAE環境でデフォルトがロードされます。　その他環境、ローカル開発時は手動で入れる必要があります）  
　app.config['SESSION_FIRESTORE_COLLECTION']に指定したコレクションに保存され、デフォルトはsessionsです。  
　app.config['SESSION_KEY_PREFIX']がドキュメントのsidキーに保存されるセッションIDの前に付与され、デフォルトはsession_です（注意：ドキュメントIDではありません）  
　Expireは呼び出し時のソフトウェア処理であり、ドキュメントの寿命は管理されていません。  必要ならexpiryキーの値で消去するタスクを組んでください。  

　デフォルトのsessionのバックエンドになるので、セッション設定以降の処理は普通のsessionとして使えます。


## Use:
```
from flask import Flask, session
from flask-firestore-session import Session

app.secret_key = 'secret'
app.config['SESSION_TYPE'] = 'firestore'
Session(app)

@app.route('/session-set')
def session-set():
  session['key'] = 'value'
  return 'Set'
  
@app.route('/session-get')
def session-get():
  value = session['key']
  return 'Value:%s' % (value)
```

## Full options:
```
from flask import Flask, session
from flask-firestore-session import Session
from google.cloud import firestore

db = firestore.client(credential)

app.secret_key = 'secret'
app.config['SESSION_TYPE'] = 'firestore'
app.config['SESSION_FIRESTORE'] = db #Firestoreクライアントを手動設定する
app.config['SESSION_FIRESTORE_COLLECTION'] = 'session' #セッションを保存するコレクション名
app.config['SESSION_KEY_PREFIX'] = 'mysession_' #SIDのプレフィクス
app.config['SESSION_USE_SIGNER'] = False #Signerの使用
app.config['SESSION_PERMANENT'] = True #寿命の有効設定
app.config['permanent_session_lifetime'] = 60*60*24*30 #寿命の秒数
Session(app)
```
