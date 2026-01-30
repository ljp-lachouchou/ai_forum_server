import os
from typing import Optional, Dict

import firebase_admin
from firebase_admin import credentials, messaging

from common.env import load_env


class FCMClient:
    _instance: Optional["FCMClient"] = None
    _app = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FCMClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, service_account_path: str = None):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._load_env(service_account_path)

    def _load_env(self, service_account_path: str = None):
        load_env()
        path = service_account_path or os.environ.get("FIREBASE_SERVICE_ACCOUNT")
        if not path:
            raise RuntimeError("Firebase service account path not provided")

        if self._app:
            return

        try:
            self._app = firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate(path)
            self._app = firebase_admin.initialize_app(cred)

    @property
    def app(self):
        return self._app

    def send_topic(
        self,
        topic: str,
        title: Optional[str] = None,
        body: Optional[str] = None,
        data: Optional[Dict[str, str]] = None,
    ) -> str:
        notification = None
        if title or body:
            notification = messaging.Notification(title=title, body=body)
        message = messaging.Message(
            notification=notification,
            data=data,
            topic=topic,
        )
        return messaging.send(message, app=self._app)
