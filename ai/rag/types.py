from typing import Iterable, Protocol, Any


class WordTagLike(Protocol):
    id: Any


class WordModelLike(Protocol):
    id: Any
    word_name: str
    author_id: Any
    category: str
    create_time: int
    word_tags: Iterable[WordTagLike]
    is_delete: bool
    word_url: str
