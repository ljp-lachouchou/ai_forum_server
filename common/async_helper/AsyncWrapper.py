import asyncio
from functools import wraps
from concurrent.futures import ThreadPoolExecutor


class AsyncWrapper:
    _io_executor = ThreadPoolExecutor(max_workers=50)
    _upload_sem = asyncio.Semaphore(10)

    @classmethod
    def to_async(cls, sem: asyncio.Semaphore = None):
        """
        同步函数转异步的装饰器
        :param sem: 传入信号量对象来控制并发
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                loop = asyncio.get_running_loop()

                # 如果传入了信号量，则进行并发控制
                if sem:
                    async with sem:
                        return await loop.run_in_executor(
                            cls._io_executor, lambda: func(*args, **kwargs)
                        )
                else:
                    # 否则直接丢进线程池
                    return await loop.run_in_executor(
                        cls._io_executor, lambda: func(*args, **kwargs)
                    )

            return wrapper

        return decorator
