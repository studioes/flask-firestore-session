# -*- coding: utf-8 -*-
"""
    flask_session_firestore

    Hideyuki Obara, 2019.
"""

__version__ = '0.1.1'

from .sessions import FirestoreSessionInterface

class Session(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.session_interface = self._get_interface(app)

    def _get_interface(self, app):
        config = app.config.copy()
        config.setdefault('SESSION_TYPE', 'null')
        config.setdefault('SESSION_PERMANENT', True)
        config.setdefault('SESSION_USE_SIGNER', False)
        config.setdefault('SESSION_KEY_PREFIX', 'session_')
        config.setdefault('SESSION_FIRESTORE', None)
        config.setdefault('SESSION_FIRESTORE_COLLECTION', 'sessions')

        if config['SESSION_TYPE'] == 'firestore':
            session_interface = FirestoreSessionInterface(
                app, config['SESSION_FIRESTORE'],
                config['SESSION_FIRESTORE_COLLECTION'],
                config['SESSION_KEY_PREFIX'], config['SESSION_USE_SIGNER'],
                config['SESSION_PERMANENT'])
        else:
            raise Exception('Unsupported session type')
            session_interface = None

        return session_interface
