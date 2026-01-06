import os
from pathlib import Path
from typing import Optional, Any, Dict
from dotenv import load_dotenv
from supabase._sync.client import SyncClient

from common.async_helper.AsyncWrapper import AsyncWrapper

default_filter = {"status": "published"}


class SupabaseClient:
    # 真正的全局单例客户端
    _instance: Optional['SupabaseClient'] = None
    _client: SyncClient = None

    def __new__(cls, *args, **kwargs):
        """确保全局只有一个 SupabaseClient 对象"""
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, url: str = None, key: str = None):
        # 只有第一次初始化时加载环境变量
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._load_env(url, key)

    def _load_env(self, url: str = None, key: str = None):
        if not self._client:
            env_path = Path(__file__).resolve().parents[1] / ".env"
            load_dotenv(dotenv_path=env_path, override=True)

            final_url = url or os.environ.get("SUPABASE_URL")
            final_key = key or os.environ.get("SUPABASE_KEY")

            if not final_url or not final_key:
                raise RuntimeError("Supabase URL or KEY not provided")

            from supabase import create_client
            # 这里的 _client 是类变量，确保全局唯一
            SupabaseClient._client = create_client(final_url, final_key)

    @property
    def client(self):
        """获取原始 Supabase 客户端的快捷方式"""
        return self._client

    def get_auth_client(self, token: Optional[str] = None):
        """
        核心改动：获取一个带身份的客户端。
        如果传入 token，返回带身份的请求句柄；否则返回默认 client。
        """
        if token:
            # 挂载 Token 到 postgrest
            self._client.postgrest.auth(token)
        return self._client

    def _insert(self, table: str, data: Dict[str, Any]):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        res = self._client.table(table).insert(data).execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, 'msg', '数据库查询失败'))

        return res.data

    def _update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any], token: str = None):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")
        client = self._client
        if token:
            client.postgrest.auth(token)
        query = self._client.table(table).update(data)
        for k, v in filters.items():
            query = query.eq(k, v)

        res = query.execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, 'msg', '数据库查询失败'))

        return res.data

    def _select(self, table: str, filters: Dict[str, Any] = None, single: bool = False):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        query = self._client.table(table).select("*")
        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)

        if single:
            query = query.single()

        res = query.execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, 'msg', '数据库查询失败'))

        return res.data

    def _mutil_select(self, table: str, tar_in_column: str, in_s: list, filters: Dict[str, Any] = None):
        """

        :param table:
        :param tar_in_column: in的目标列
        :param in_s: in的集合
        :param filters:
        :return:
        """
        if not self._client:
            return
        query = self._client.table(table) \
            .select("*") \
            .in_(tar_in_column, [str(i) for i in in_s])
        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)
        res = query.execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, 'msg', '数据库查询失败'))

            # 如果 res 是 Supabase 的 postgrest.base_request.APIResponse
            # 通常如果没有抛出异常，可以直接返回 data
        return getattr(res, 'data', [])

    def _rpc(self, fn_name: str, params: Dict[str, Any]):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        res = self._client.rpc(fn_name, params).execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, 'msg', '数据库查询失败'))

        return res.data

    def _delete(self, table: str, filters: Dict[str, Any]):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        query = self._client.table(table).delete()
        for k, v in filters.items():
            query = query.eq(k, v)

        res = query.execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, 'msg', '数据库查询失败'))

        return res.data

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def insert_async(self, table: str, data: Dict[str, Any]):
        return self._insert(table, data)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def update_async(self, table: str, data: Dict[str, Any], filters: Dict[str, Any], token: str = None):
        return self._update(table, data, filters, token)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def select_async(
            self,
            table: str,
            filters: Dict[str, Any] = None,
            single: bool = False
    ):
        return self._select(table, filters, single)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def rpc_async(self, fn_name: str, params: Dict[str, Any]):
        return self._rpc(fn_name, params)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def delete_async(self, table: str, filters: Dict[str, Any]):
        return self._delete(table, filters)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def mutil_select_async(self, table: str, tar_in_column: str, in_s: list, filters: Dict[str, Any]):
        return self._mutil_select(table, tar_in_column, in_s, filters)
