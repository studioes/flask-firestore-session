# -*- coding: utf-8 -*-
"""
    flask_session_firestore.sessions
    
    Hideyuki Obara, 2019.
"""
import sys
import time
from datetime import datetime, timezone
from uuid import uuid4
try:
    import cPickle as pickle
except ImportError:
    import pickle

from flask.sessions import SessionInterface as FlaskSessionInterface
from flask.sessions import SessionMixin
from werkzeug.datastructures import CallbackDict
from itsdangerous import Signer, BadSignature, want_bytes


PY2 = sys.version_info[0] == 2
if not PY2:
    text_type = str
else:
    text_type = unicode


def total_seconds(td):
    return td.days * 60 * 60 * 24 + td.seconds


class ServerSideSession(CallbackDict, SessionMixin):
    """Baseclass for server-side based sessions."""

    def __init__(self, initial=None, sid=None, permanent=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        if permanent:
            self.permanent = permanent
        self.modified = False


class FirestoreSession(ServerSideSession):
    pass


class SessionInterface(FlaskSessionInterface):

    def _generate_sid(self):
        return str(uuid4())

    def _get_signer(self, app):
        if not app.secret_key:
            return None
        return Signer(app.secret_key, salt='flask-session',
                      key_derivation='hmac')


class FirestoreSessionInterface(SessionInterface):
    """Uses the Firestore from a flask app as a session backend.

    :param app: A Flask app instance.
    :param db: A Flask-Firestore instance.
    :param collection: The collection name you want to use.
    :param key_prefix: A prefix that is added to all store keys.
    :param use_signer: Whether to sign the session id cookie or not.
    :param permanent: Whether to use permanent session or not.
    """

    serializer = pickle
    session_class = FirestoreSession


    def __init__(self, app, db, collection, key_prefix, use_signer=False,
                 permanent=True):

        if db is None:
            db = firestore.client()

        self.db = db
        self.collection = collection
        self.key_prefix = key_prefix
        self.use_signer = use_signer
        self.permanent = permanent


    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self._generate_sid()
            return self.session_class(sid=sid, permanent=self.permanent)
        if self.use_signer:
            signer = self._get_signer(app)
            if signer is None:
                return None
            try:
                sid_as_bytes = signer.unsign(sid)
                sid = sid_as_bytes.decode()
            except BadSignature:
                sid = self._generate_sid()
                return self.session_class(sid=sid, permanent=self.permanent)

        store_id = self.key_prefix + sid
        documents = self.db.collection(self.collection).where('sid', '==', store_id).get()
        try:
            saved_session = next(documents)
        except StopIteration:
            # not exists
            saved_session = None
        if saved_session:
            saved_dict = saved_session.to_dict()
            if not saved_dict['expiry'] is None:
                if saved_dict['expiry'] <= datetime.now(timezone.utc):
                    self.db.collection(self.collection).document(saved_session.id()).delete()
                    saved_session = None
        if saved_session:
            try:
                val = saved_dict['data']
                data = self.serializer.loads(want_bytes(val))
                return self.session_class(data, sid=sid)
            except:
                return self.session_class(sid=sid, permanent=self.permanent)
        return self.session_class(sid=sid, permanent=self.permanent)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        store_id = self.key_prefix + session.sid
        documents = self.db.collection(self.collection).where('sid', '==', store_id).get()

        try:
            saved_session = next(documents)
        except StopIteration:
            # not exists
            saved_session = False

        if not session:
            if session.modified:
                if saved_session:
                    saved_session.db.collection(self.collection).document(saved_session.id).delete()
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain, path=path)
            return

        httponly = self.get_cookie_httponly(app)
        secure = self.get_cookie_secure(app)
        expires = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        if saved_session:
            self.db.collection(self.collection).document(saved_session.id).update({'data': val,\
                                                                                   'expiry': expires})
        else:
            self.db.collection(self.collection).add(
                {'sid':store_id,
                 'data':val,
                 'expiry':expires}
            )
        if self.use_signer:
            session_id = self._get_signer(app).sign(want_bytes(session.sid))
        else:
            session_id = session.sid
        response.set_cookie(app.session_cookie_name, session_id,
                            expires=expires, httponly=httponly,
                            domain=domain, path=path, secure=secure)
