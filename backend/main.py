import uvicorn
from fastapi import FastAPI

from backend.api.WordApi import word_router

app = FastAPI(title="智汇社区 AI 后端")

# 挂载路由
app.include_router(word_router)

if __name__ == "__main__":
    # 启动命令：python main.py
    # 运行后访问 http://127.0.0.1:8000/docs 查看 Swagger 文档
    uvicorn.run(app, host="0.0.0.0", port=8000)