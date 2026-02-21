from uuid import UUID

from backend.Sql.SClient import SupabaseClient
from backend.entity.profile import ProfileSchema
from common.async_helper.AsyncWrapper import AsyncWrapper


class ProfileService:
    def __init__(self, sb: SupabaseClient):
        self.sb = sb

    def set_auth(self, token: str):
        """挂载用户 Token，确保 RLS 策略生效"""

        return None

    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def get_profile(self, user_id: UUID, token: str = None):
        """获取指定 ID 的用户信息"""
        client = self.sb.get_auth_client(token)
        res = client.table("profiles").select("*").eq("id", str(user_id)).single().execute()
        return res.data

    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def get_profile_by_profile_account(self, profile_account: str):
        """根据email获取user"""
        res = self.sb.client.table("profiles").select("*") \
            .eq("profile_account", profile_account) \
            .maybe_single() \
            .execute()
        if hasattr(res,"data"):
            return res.data
        else:
            return None

    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def update_profile(self, user_id: UUID, data: dict, token: str = None):
        """更新用户信息 (受 RLS: auth.uid() = id 保护)"""
        client = self.sb.get_auth_client(token)
        res = client.table("profiles").update(data).eq("id", str(user_id)).execute()
        return res.data

    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def upsert_profile(self, profile_data: ProfileSchema):
        """创建或覆盖用户信息"""
        res = self.sb.client.table("profiles").upsert(profile_data.model_dump(mode='json')).execute()
        return res.data

    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def insert_profile(self, profile_data: ProfileSchema):
        """创建或覆盖用户信息"""
        res = self.sb.client.table("profiles").insert(profile_data.model_dump(mode='json')).execute()
        return res.data
