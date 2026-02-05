import sys
import types
import unittest
from pathlib import Path


_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

_jpush = types.ModuleType("jpush")
_common = types.ModuleType("jpush.common")
_jpush.__path__ = []
_jpush.common = _common

_sent = []


class _DummyPush:
    def __init__(self):
        self.audience = None
        self.platform = None
        self.notification = None
        self.message = None

    def send(self):
        _sent.append(self)
        return "msg-id"


class _DummyClient:
    def __init__(self, app_key, master_secret):
        self.app_key = app_key
        self.master_secret = master_secret

    def create_push(self):
        return _DummyPush()


class _DummyNotification:
    def __init__(self, alert=None, android=None, ios=None):
        self.alert = alert
        self.android = android
        self.ios = ios


class _DummyAndroid:
    def __init__(self, alert=None, title=None, extras=None):
        self.alert = alert
        self.title = title
        self.extras = extras


class _DummyIOS:
    def __init__(self, alert=None, extras=None):
        self.alert = alert
        self.extras = extras


class _DummyMessage:
    def __init__(self, msg_content="", extras=None):
        self.msg_content = msg_content
        self.extras = extras


class _Unauthorized(Exception):
    pass


class _APIConnectionException(Exception):
    pass


class _JPushFailure(Exception):
    pass


_jpush.JPush = _DummyClient
_jpush.all_ = object()
_jpush.notification = (
    lambda alert=None, android=None, ios=None: _DummyNotification(
        alert=alert, android=android, ios=ios
    )
)
_jpush.android = (
    lambda alert=None, title=None, extras=None: _DummyAndroid(
        alert=alert, title=title, extras=extras
    )
)
_jpush.ios = lambda alert=None, extras=None: _DummyIOS(alert=alert, extras=extras)
_jpush.message = (
    lambda msg_content="", extras=None: _DummyMessage(
        msg_content=msg_content, extras=extras
    )
)

_common.Unauthorized = _Unauthorized
_common.APIConnectionException = _APIConnectionException
_common.JPushFailure = _JPushFailure

sys.modules["jpush"] = _jpush
sys.modules["jpush.common"] = _common

from backend.Sql.FCMClient import FCMClient


class FCMClientTests(unittest.TestCase):
    def setUp(self):
        global _sent
        _sent = []

    def test_send_topic_with_data(self):
        client = FCMClient()
        resp = client.send_topic("sync", data={"type": "sync"})

        self.assertEqual(resp, "msg-id")
        self.assertEqual(len(_sent), 1)
        push = _sent[0]
        self.assertIsNone(push.notification)
        self.assertIsNotNone(push.message)
        self.assertEqual(push.message.extras, {"type": "sync"})
        self.assertIs(push.audience, _jpush.all_)
        self.assertIs(push.platform, _jpush.all_)

    def test_send_topic_with_notification(self):
        client = FCMClient()
        client.send_topic("news", title="t", body="b")

        push = _sent[0]
        self.assertIsNotNone(push.notification)
        self.assertEqual(push.notification.alert, "b")
        self.assertIs(push.audience, _jpush.all_)
        self.assertIs(push.platform, _jpush.all_)


if __name__ == "__main__":
    client = FCMClient()
    resp = client.send_topic("news", title="t", body="b")
    print(resp)
