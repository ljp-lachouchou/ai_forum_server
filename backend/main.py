import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import asyncio
import os
from contextlib import asynccontextmanager
import logging
import uvicorn
from fastapi import FastAPI

from backend.api.AuthApi import auth_router
from backend.api.CommentApi import comment_router
from backend.api.InteractionApi import interaction_router
from backend.api.PersonaApi import persona_router
from backend.api.ProfileApi import profile_router
from backend.api.TreeholeApi import treehole_router
from backend.api.WordApi import word_router
from backend.api.NotificationApi import notification_router
from backend.api.SyncApi import sync_router
from backend.api.FollowApi import follow_router
from backend.api.ReportApi import report_router
from backend.api.StorageApi import storage_router
from backend.api.services import warmup_ai_models
from backend.service.ChangeLogNotifier import ChangeLogNotifier
from backend.Sql.FCMClient import FCMClient
from backend.Sql.SClient import SupabaseClient
from common.env import load_env

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_env()
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(
            level=os.environ.get("LOG_LEVEL", "INFO").upper(),
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
        )
    enabled = os.environ.get("CHANGE_LOG_NOTIFIER_ENABLED", "true").lower() in ("1", "true", "yes")
    ai_warmup_enabled = os.environ.get("AI_WARMUP_ENABLED", "true").lower() in ("1", "true", "yes")

    if ai_warmup_enabled:
        await warmup_ai_models()
    else:
        _logger.info("ai warmup disabled")

    notifier = None
    task = None
    if enabled:
        try:
            notifier = ChangeLogNotifier(
                SupabaseClient(),
                FCMClient(),
                topic=os.environ.get("CHANGE_LOG_NOTIFIER_TOPIC", "sync"),
                poll_interval=float(os.environ.get("CHANGE_LOG_NOTIFIER_POLL_INTERVAL", "1.0")),
                batch_size=int(os.environ.get("CHANGE_LOG_NOTIFIER_BATCH_SIZE", "200")),
                start_from_latest=os.environ.get("CHANGE_LOG_NOTIFIER_START_FROM_LATEST", "true").lower() in ("1", "true", "yes"),
            )
            app.state.change_log_notifier = notifier
            task = asyncio.create_task(notifier.run())
            app.state.change_log_notifier_task = task
            _logger.info("change_log notifier started")
        except Exception:
            # If Supabase/FCM is not configured, skip starting the notifier.
            notifier = None
            task = None
            _logger.exception("change_log notifier failed to start")
    else:
        _logger.info("change_log notifier disabled")

    try:
        yield
    finally:
        if notifier:
            notifier.stop()
        if task:
            task.cancel()
        if notifier or task:
            _logger.info("change_log notifier stopped")


app = FastAPI(title="Forum AI Backend", lifespan=lifespan)


# 挂载路由
app.include_router(word_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(persona_router)
app.include_router(comment_router)
app.include_router(interaction_router)
app.include_router(treehole_router)
app.include_router(notification_router)
app.include_router(sync_router)
app.include_router(follow_router)
app.include_router(report_router)
app.include_router(storage_router)
if __name__ == "__main__":
    # 启动命令：python main.py
    # 运行后访问 http://127.0.0.1:8000/docs 查看 Swagger 文档
    uvicorn.run(app, host="0.0.0.0", port=9000)
