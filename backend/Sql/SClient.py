import os
from typing import Optional, Any, Dict

from supabase._sync.client import SyncClient

from common.async_helper.AsyncWrapper import AsyncWrapper
from common.env import load_env

default_filter = {"status": "published"}


class SupabaseClient:
    # 真正的全局单例客户端
    _instance: Optional['SupabaseClient'] = None
    _client: SyncClient = None
    _url: Optional[str] = None
    _key: Optional[str] = None
    _anon_key: Optional[str] = None
    _service_role_key: Optional[str] = None

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
            load_env()

            final_url = url or os.environ.get("SUPABASE_URL")
            final_key = key or os.environ.get("SUPABASE_KEY")
            final_anon_key = os.environ.get("SUPABASE_ANON_KEY")
            final_service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

            if not final_url or not final_key:
                raise RuntimeError("Supabase URL or KEY not provided")

            from supabase import create_client
            SupabaseClient._url = final_url
            SupabaseClient._key = final_key
            SupabaseClient._anon_key = final_anon_key
            SupabaseClient._service_role_key = final_service_role_key
            # 这里的 _client 是类变量，确保全局唯一
            SupabaseClient._client = create_client(final_url, final_key)

    @property
    def client(self):
        """获取原始 Supabase 客户端的快捷方式"""
        return self._client

    def get_anon_client(self):
        """
        Use anon/publishable key client for Auth endpoints.
        Falls back to SUPABASE_KEY when anon key is absent.
        """
        if not self._url or not self._key:
            raise RuntimeError("Supabase URL or KEY not provided")
        from supabase import create_client
        key = self._anon_key or self._key
        return create_client(self._url, key)

    def get_auth_client(self, token: Optional[str] = None):
        """
        Get a client with auth token bound. If token is None, return default client.
        """
        if not token:
            return self._client
        if not self._url or not self._key:
            raise RuntimeError("Supabase URL or KEY not provided")
        # Use server key for apikey header; user JWT is still carried in Authorization.
        key = self._key
        from supabase import create_client
        client = create_client(self._url, key)
        pg = client.postgrest.auth(token)
        if pg is not None:
            # Ensure apikey + Authorization headers exist on the auth-bound client.
            try:
                target = getattr(pg, "session", None) or getattr(pg, "client", None)
                headers = getattr(target, "headers", None) if target is not None else None
                if headers is not None:
                    headers["apikey"] = key
                    headers["Authorization"] = f"Bearer {token}"
            except Exception:
                pass
            try:
                client.postgrest = pg
            except Exception:
                pass
        return client

    def get_service_role_client(self):
        if not self._url or not self._key:
            raise RuntimeError("Supabase URL or KEY not provided")
        service_key = self._service_role_key or self._key
        from supabase import create_client
        client = create_client(self._url, service_key)
        pg = client.postgrest.auth(service_key)
        if pg is not None:
            try:
                target = getattr(pg, "session", None) or getattr(pg, "client", None)
                headers = getattr(target, "headers", None) if target is not None else None
                if headers is not None:
                    headers["apikey"] = service_key
                    headers["Authorization"] = f"Bearer {service_key}"
            except Exception:
                pass
            try:
                client.postgrest = pg
            except Exception:
                pass
        return client

    def _insert(self, table: str, data: Dict[str, Any], token: str = None):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        client = self.get_auth_client(token)
        res = client.table(table).insert(data).execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, "msg", "database query failed"))

        return res.data

    def _insert_service(self, table: str, data: Dict[str, Any]):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")
        client = self.get_service_role_client()
        res = client.table(table).insert(data).execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, "msg", "database query failed"))
        return res.data

    def _update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any], token: str = None):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")
        client = self.get_auth_client(token)
        query = client.table(table).update(data)
        for k, v in filters.items():
            query = query.eq(k, v)

        res = query.execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, "msg", "database query failed"))

        return res.data

    def _select(
            self,
            table: str,
            filters: Dict[str, Any] = None,
            single: bool = False,
            order_by: Optional[str] = None,
            desc: bool = False,
            token: str = None,
    ):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        client = self.get_auth_client(token)
        query = client.table(table).select("*")
        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            query = query.single()

        res = query.execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, "msg", "database query failed"))

        return res.data

    def _mutil_select(self, table: str, tar_in_column: str, in_s: list, filters: Dict[str, Any] = None, token: str = None):
        """

        :param table:
        :param tar_in_column: in的目标列
        :param in_s: in的集合
        :param filters:
        :return:
        """
        if not self._client:
            return
        client = self.get_auth_client(token)
        query = client.table(table) \
            .select("*") \
            .in_(tar_in_column, [str(i) for i in in_s])
        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)
        res = query.execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, "msg", "database query failed"))

            # 如果 res 是 Supabase 的 postgrest.base_request.APIResponse
            # 通常如果没有抛出异常，可以直接返回 data
        return getattr(res, 'data', [])

    def _rpc(self, fn_name: str, params: Dict[str, Any], token: str = None):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        client = self.get_auth_client(token)
        res = client.rpc(fn_name, params).execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, "msg", "database query failed"))

        return res.data

    def _delete(self, table: str, filters: Dict[str, Any], token: str = None):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        client = self.get_auth_client(token)
        query = client.table(table).delete()
        for k, v in filters.items():
            query = query.eq(k, v)

        res = query.execute()
        if hasattr(res, 'code') and res.code != 200:
            raise RuntimeError(getattr(res, "msg", "database query failed"))

        return res.data

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def insert_async(self, table: str, data: Dict[str, Any], token: str = None):
        return self._insert(table, data, token)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def insert_service_async(self, table: str, data: Dict[str, Any]):
        return self._insert_service(table, data)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def update_async(self, table: str, data: Dict[str, Any], filters: Dict[str, Any], token: str = None):
        return self._update(table, data, filters, token)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def select_async(
            self,
            table: str,
            filters: Dict[str, Any] = None,
            single: bool = False,
            order_by: Optional[str] = None,
            desc: bool = False,
            token: str = None,
    ):
        return self._select(table, filters, single, order_by, desc, token)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def rpc_async(self, fn_name: str, params: Dict[str, Any], token: str = None):
        return self._rpc(fn_name, params, token)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def delete_async(self, table: str, filters: Dict[str, Any], token: str = None):
        return self._delete(table, filters, token)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def mutil_select_async(self, table: str, tar_in_column: str, in_s: list, filters: Dict[str, Any], token: str = None):
        return self._mutil_select(table, tar_in_column, in_s, filters, token)
