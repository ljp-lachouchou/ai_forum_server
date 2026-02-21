import re

from fastapi import HTTPException
from gotrue import User, AuthResponse

from backend.Sql.SClient import SupabaseClient
from common.async_helper.AsyncWrapper import AsyncWrapper


class AuthService:
    def __init__(self):
        # 鑾峰彇鍏ㄥ眬鍗曚緥鐨?Supabase 瀹㈡埛绔?
        self.sb = SupabaseClient()
        self.client = self.sb.get_anon_client()



    def check_pwd(self, pwd):
        """
        闀垮害 8-16 浣嶏紝蹇呴』鍖呭惈澶у皬鍐欏瓧姣嶃€佹暟瀛楀拰鐗规畩瀛楃
        :param pwd:
        :return:
        """
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,16}$"
        if not re.match(pattern, pwd):
            raise HTTPException(
                status_code=400,
                detail="密码格式不正确：需包含大小写字母、数字和特殊字符，长度 6-16 位",
            )
        return True

    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def login(self, email, password):
        """处理登录并返回会话信息"""
        res = self.client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        token = res.session.access_token if getattr(res, "session", None) else None
        user_id = getattr(getattr(res, "user", None), "id", None)
        if not token or not user_id:
            raise HTTPException(status_code=401, detail="登录失败：未获取到有效会话")
        return {"access_token": token, "user_id": str(user_id)}

    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def register(self, email, password)->AuthResponse:
        """鐢ㄦ埛娉ㄥ唽"""
        return self.client.auth.sign_up({"email": email, "password": password})



    @AsyncWrapper.to_async(AsyncWrapper._upload_sem)
    def get_current_user(self, token: str)->User:
        return self.client.auth.get_user(token)

