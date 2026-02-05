import os
from typing import Optional, Dict

import jpush
from jpush import common

from common.env import load_env


class FCMClient:
    _instance: Optional["FCMClient"] = None
    _client = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FCMClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, app_key: str = None, master_secret: str = None, **kwargs):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            if app_key is None:
                app_key = kwargs.get("service_account_path")
            self._load_env(app_key, master_secret)

    def _load_env(self, app_key: str = None, master_secret: str = None):
        load_env()
        app_key = app_key or os.environ.get("APP_KEY")
        master_secret = master_secret or os.environ.get("MASTER_SECRET")
        if not app_key or not master_secret:
            raise RuntimeError("JPush APP_KEY/MASTER_SECRET not provided")

        if self._client:
            return

        self._client = jpush.JPush(app_key, master_secret)

    @property
    def app(self):
        return self._client

    def send_topic(
        self,
        topic: str,
        title: Optional[str] = None,
        body: Optional[str] = None,
        data: Optional[Dict[str, str]] = None,
    ) -> str:
        push = self._client.create_push()
        push.audience = jpush.all_
        push.platform = jpush.all_

        alert = body or title or ""
        extras = data or None

        if title or body:
            if extras:
                android = jpush.android(alert=alert, title=title, extras=extras)
                ios = jpush.ios(alert=alert, extras=extras)
                push.notification = jpush.notification(
                    alert=alert,
                    android=android,
                    ios=ios,
                )
            else:
                push.notification = jpush.notification(alert=alert)
        elif extras:
            push.message = jpush.message("", extras=extras)

        try:
            response = push.send()
        except common.Unauthorized:
            raise common.Unauthorized("Unauthorized")
        except common.APIConnectionException:
            raise common.APIConnectionException("conn")
        except common.JPushFailure:
            print("JPushFailure")
            response = None
        except Exception:
            print("Exception")
            response = None
        return response
