import os
from pathlib import Path
from typing import Optional, Any, Dict
from dotenv import load_dotenv
from supabase import create_client, Client
from io import StringIO

from common.async_helper.AsyncWrapper import AsyncWrapper

default_filter = {"status": "published"}

class SupabaseClient:
    _client: Optional[Client] = None

    def __init__(self, url: str = None, key: str = None):
        self.__url = url
        self.__key = key
        self.__request_semaphore = AsyncWrapper._upload_sem

    def init_client(self):
        if not self._client:
            env_path = Path(__file__).resolve().parents[1] / ".env"

            print("=== SupabaseClient DEBUG ===")
            print("SClient.py path:", Path(__file__).resolve())
            print("Calculated env path:", env_path)
            print("Env exists:", env_path.exists())
            print("CWD:", os.getcwd())

            load_dotenv(dotenv_path=env_path, override=True)

            print("SUPABASE_URL from env:", os.environ.get("SUPABASE_URL"))
            print("SUPABASE_KEY from env:", os.environ.get("SUPABASE_KEY"))
            print("============================")

            url = self.__url or os.environ.get("SUPABASE_URL")
            key = self.__key or os.environ.get("SUPABASE_KEY")

            if not url or not key:
                raise RuntimeError("Supabase URL or KEY not provided")

            from supabase import create_client
            self._client = create_client(url, key)

        return self

    def _insert(self, table: str, data: Dict[str, Any]):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        res = self._client.table(table).insert(data).execute()
        if res.error:
            raise RuntimeError(res.error.message)

        return res.data

    def _update(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        query = self._client.table(table).update(data)
        for k, v in filters.items():
            query = query.eq(k, v)

        res = query.execute()
        if res.error:
            raise RuntimeError(res.error.message)

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
        if res.error:
            raise RuntimeError(res.error.message)

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
        if res.error:
            raise RuntimeError(res.error.message)

        return res.data

    def _delete(self, table: str, filters: Dict[str, Any]):
        if not self._client:
            raise RuntimeError("Supabase client not initialized")

        query = self._client.table(table).delete()
        for k, v in filters.items():
            query = query.eq(k, v)

        res = query.execute()
        if res.error:
            raise RuntimeError(res.error.message)

        return res.data

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def insert_async(self, table: str, data: Dict[str, Any]):
        return self._insert(table, data)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def update_async(self, table: str, data: Dict[str, Any], filters: Dict[str, Any]):
        return self._update(table, data, filters)

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
    def mutil_select_async(self, table: str,tar_in_column:str,in_s:list, filters: Dict[str, Any]):
        return self._mutil_select(table,tar_in_column,in_s, filters)


