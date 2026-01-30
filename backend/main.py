import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

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

app = FastAPI(title="智汇社区 AI 后端")

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
if __name__ == "__main__":
    # 启动命令：python main.py
    # 运行后访问 http://127.0.0.1:8000/docs 查看 Swagger 文档
    uvicorn.run(app, host="0.0.0.0", port=8000)
