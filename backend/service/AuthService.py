import re

from fastapi import HTTPException
from gotrue import User, AuthResponse

from backend.Sql.SClient import SupabaseClient
from common.async_helper.AsyncWrapper import AsyncWrapper


class AuthService:
    def __init__(self):
        # 获取全局单例的 Supabase 客户端
        self.sb = SupabaseClient()
        self.client = self.sb.client



    def check_pwd(self, pwd):
        """
        长度 8-16 位，必须包含大小写字母、数字和特殊字符
        :param pwd:
        :return:
        """
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,16}$"
        if not re.match(pattern, pwd):
            raise HTTPException(
                status_code=400,
                detail="密码格式不正确：须包含大小写字母、数字和特殊字符，长度6-16位"
            )
        return True

    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def login(self, email, password):
        """处理登录并返回 Session"""
        # 这里的 sign_in_with_password 是 Supabase 官方 Auth 接口
        res = self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        # 返回 access_token，后续所有 RLS 操作都需要它
        return res.session.access_token

    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def register(self, email, password)->AuthResponse:
        """用户注册"""
        return self.client.auth.sign_up({"email": email, "password": password})



    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def get_current_user(self, token: str)->User:
        return self.client.auth.get_user(token)
