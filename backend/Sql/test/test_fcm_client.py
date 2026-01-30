import sys
import types
import unittest
from pathlib import Path


_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

_firebase_admin = types.ModuleType("firebase_admin")
_credentials = types.ModuleType("firebase_admin.credentials")
_messaging = types.ModuleType("firebase_admin.messaging")


class _DummyApp:
    pass


class _DummyCred:
    def __init__(self, path):
        self.path = path


_app = None
_sent = []


def _get_app():
    if _app is None:
        raise ValueError("not initialized")
    return _app


def _initialize_app(cred):
    global _app
    _app = _DummyApp()
    _app.cred = cred
    return _app


def _certificate(path):
    return _DummyCred(path)


class _Notification:
    def __init__(self, title=None, body=None):
        self.title = title
        self.body = body


class _Message:
    def __init__(self, notification=None, data=None, topic=None):
        self.notification = notification
        self.data = data
        self.topic = topic


def _send(message, app=None):
    _sent.append((message, app))
    return "msg-id"


_firebase_admin.get_app = _get_app
_firebase_admin.initialize_app = _initialize_app
_credentials.Certificate = _certificate
_messaging.Notification = _Notification
_messaging.Message = _Message
_messaging.send = _send

sys.modules["firebase_admin"] = _firebase_admin
sys.modules["firebase_admin.credentials"] = _credentials
sys.modules["firebase_admin.messaging"] = _messaging

from backend.Sql.FCMClient import FCMClient


class FCMClientTests(unittest.TestCase):
    def setUp(self):
        global _app, _sent
        _app = None
        _sent = []

    def test_send_topic_with_data(self):
        client = FCMClient()
        resp = client.send_topic("sync", data={"type": "sync"})

        self.assertEqual(resp, "msg-id")
        self.assertEqual(len(_sent), 1)
        message, app = _sent[0]
        self.assertEqual(message.topic, "sync")
        self.assertEqual(message.data, {"type": "sync"})
        self.assertIsNotNone(app)

    def test_send_topic_with_notification(self):
        client = FCMClient()
        client.send_topic("news", title="t", body="b")

        message, _ = _sent[0]
        self.assertEqual(message.notification.title, "t")
        self.assertEqual(message.notification.body, "b")


if __name__ == "__main__":
   client = FCMClient()
   resp = client.send_topic("news", title="t", body="b")
   print(resp)
