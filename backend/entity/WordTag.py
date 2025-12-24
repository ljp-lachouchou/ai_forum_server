import time

from pydantic import BaseModel, Field


class WordTag(BaseModel):
    id:str = Field(...,description="标签id")
    display_content:str = Field(...,description="用于展示的内容")
    create_time:int =  Field(default_factory=lambda: int(time.time()), description="创建时间戳")
