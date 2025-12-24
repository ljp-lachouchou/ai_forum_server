import asyncio
import os
from io import StringIO
from typing import Optional

import tos
from dotenv import load_dotenv
from tos import TosClientV2, HttpMethodType

from common.async_helper.AsyncWrapper import AsyncWrapper
from common.uuid.UUIDUtil import UUIDUtil


class TClient:
    __client:Optional[TosClientV2] = None
    def __init__(self,bucket_name:str,endpoint = 'tos-cn-beijing.volces.com',region = 'cn-beijing'):
        self.__bucket_name = bucket_name
        self.__endpoint = endpoint
        self.__region = region
        self.__upload_semaphore = asyncio.Semaphore(10)
    def init_client(self):
        if  not self.__client:
            load_dotenv()
            sk = os.environ.get('TOS_SECRET_KEY')
            ak = os.environ.get('TOS_ACCESS_KEY')
            self.__client = TosClientV2(ak, sk, self.__endpoint, self.__region)
        return self
    def _upload_char_flow(self,content:StringIO,file_name:str)->bool:
        try:
            if not self.__client:
                raise tos.exceptions.TosClientError("客户端为初始化")
            # 若在上传对象时设置文件存储类型（x-tos-storage-class）和访问权限 (x-tos-acl), 请在 put_object中设置相关参数
            # 用户在上传对象时，可以自定义元数据，以便对对象进行自定义管理
            # result = client.put_object(bucket_name, object_key, content=content, acl=tos.ACLType.ACL_Private, storage_class=tos.StorageClassType.Storage_Class_Standard, meta={'name': '张三', 'age': '20'})
            object_key = UUIDUtil.generate_object_key(file_name)
            result = self.__client.put_object(self.__bucket_name,object_key , content=content)
            # HTTP状态码
            print('http status code:{}'.format(result.status_code))
            # 请求ID。请求ID是本次请求的唯一标识，建议在日志中添加此参数
            print('request_id: {}'.format(result.request_id))
            # hash_crc64_ecma 表示该对象的64位CRC值, 可用于验证上传对象的完整性
            print('crc64: {}'.format(result.hash_crc64_ecma))
            if result.status_code == 200:
                return True
            else:
                return False
        except tos.exceptions.TosClientError as e:
            # 操作失败，捕获客户端异常，一般情况为非法请求参数或网络异常
            print('fail with client error, message:{}, cause: {}'.format(e.message, e.cause))
            return False
        except tos.exceptions.TosServerError as e:
            # 操作失败，捕获服务端异常，可从返回信息中获取详细错误信息
            print('fail with server error, code: {}'.format(e.code))
            # request id 可定位具体问题，强烈建议日志中保存
            print('error with request id: {}'.format(e.request_id))
            print('error with message: {}'.format(e.message))
            print('error with http code: {}'.format(e.status_code))
            print('error with ec: {}'.format(e.ec))
            print('error with request url: {}'.format(e.request_url))
            return False
        except Exception as e:
            print('fail with unknown error: {}'.format(e))
            return False
    def _get_pre_signed_url(self,url:str):
        ok = url.split('/')[-1]
        url_vo = self.__client.pre_signed_url(HttpMethodType.Http_Method_Get, self.__bucket_name, ok)
        return url_vo.signed_url

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def get_pre_signed_url(self,url):
        return self._get_pre_signed_url(url)

    @AsyncWrapper.to_async(sem=AsyncWrapper._upload_sem)
    def upload_char_flow_async(self, content, file_name):
        return self._upload_char_flow(content,file_name)


if __name__ == "__main__":
    rl = asyncio.run(TClient("ai-forum-word").init_client()
                     .get_pre_signed_url('https://ai-forum-word.tos-cn-beijing.volces.com/r20251224-0ec7051e-test.md'))
    print(rl)