import time
from typing import List, Optional

from pydantic import BaseModel, Field

from backend.entity.WordTag import WordTag


class MDWord(BaseModel):
    id:str = Field(...,description="文档的唯一标识")
    word_name:str = Field(...,description="文档的标题")
    author_id:str = Field(...,description="作者的id")
    word_url:str = Field(...,description="文档的url")
    word_tags:List[WordTag] = Field(default_factory=list, description="文档的标签")
    likes: int = Field(default=0, description="点赞数")
    views: int = Field(default=0, description="阅读量")
    create_time:int =  Field(default_factory=lambda: int(time.time()), description="创建时间戳")
    is_delete:bool = Field(...,description="是否被删除")
    category: str = Field(default="default", description="文档分类")
    ext_data: Optional[dict] = Field(default_factory=dict, description="预留扩展字段")

