import os
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv
from upstash_redis import Redis as SyncRedis
from upstash_redis.asyncio import Redis as AsyncRedis

class RedisCacheClient:
    # 全局单例
    _instance: Optional['RedisCacheClient'] = None
    _sync_client: Optional[SyncRedis] = None
    _async_client: Optional[AsyncRedis] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisCacheClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, url: str = None, token: str = None):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._load_env(url, token)

    def _load_env(self, url: str = None, token: str = None):
        # 加载环境变量
        env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(dotenv_path=env_path, override=True)

        final_url = url or os.environ.get("UPSTASH_REDIS_URL")
        final_token = token or os.environ.get("UPSTASH_REDIS_TOKEN")

        if not final_url or not final_token:
            raise RuntimeError("Upstash Redis URL or TOKEN not provided")

        # 初始化同步和异步客户端
        if not self._sync_client:
            RedisCacheClient._sync_client = SyncRedis(url=final_url, token=final_token)
        if not self._async_client:
            RedisCacheClient._async_client = AsyncRedis(url=final_url, token=final_token)

    @property
    def client(self) -> AsyncRedis:
        """默认返回异步客户端，适配 FastAPI 的异步环境"""
        return self._async_client

    @property
    def sync_client(self) -> SyncRedis:
        """返回同步客户端"""
        return self._sync_client

    # --- 快捷操作方法封装 ---

    async def set_token(self, jti: str, user_id: str, ex: Optional[int] = None):
        """专门用于存储 Token 的快捷方法"""
        if not ex:
            ex = int(os.environ.get("TOKEN_EXPIRE"))
        key = f"auth:token:{jti}"
        await self._async_client.set(key, user_id, ex=ex)

    async def set_token_with_single_login(self, token: str, user_id: str , ex: Optional[int] = None):
        if not ex:
            ex = int(os.environ.get("TOKEN_EXPIRE"))
        # 定义 Key 映射
        user_token_key = f"user:active_token:{user_id}"  # 记录该用户当前合法的 jti
        new_auth_key = f"auth:token:{token}"  # 实际校验用的 key

        # 2. 查找并清理旧 Token
        old_jti = await self.client.get(user_token_key)
        if old_jti:
            # 如果有旧的 jti，直接从 Redis 中删除，使其失效
            await self.client.delete(f"auth:token:{old_jti}")

        # 3. 存储新 Token
        # 存储校验键
        await self.client.set(new_auth_key, user_id, ex=ex)
        # 更新用户的当前合法 jti 记录
        await self.client.set(user_token_key, token, ex=ex)

        return True

    async def is_token_valid(self, jti: str) -> bool:
        """检查 Token 是否存在（未黑名单或未过期）"""
        key = f"auth:token:{jti}"
        return await self._async_client.exists(key) > 0

    async def delete_token(self, jti: str):
        """删除 Token (注销)"""
        await self._async_client.delete(f"auth:token:{jti}")

    async def get_value(self, key: str) -> Any:
        return await self._async_client.get(key)