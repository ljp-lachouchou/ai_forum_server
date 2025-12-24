from backend.entity.MDword import MDWord


def content_mapper(chunk, dense, sparse, word_model: MDWord):
    return {
                    "word_id": str(word_model.id),
                    "raw_text": chunk.page_content,
                    "dense_vector": dense,
                    "sparse_vector": sparse,
                    "entity_info": {
                        "word_name": word_model.word_name,
                        "author_id": word_model.author_id,
                        "category": word_model.category,
                        "create_time": word_model.create_time,
                        "tags": [tag.id for tag in word_model.word_tags],
                        "is_delete": word_model.is_delete
                    }
                }

def title_mapper(chunk, dense, sparse,word_model:MDWord):
    return {
        "word_id": str(word_model.id),
        "title": word_model.word_name,
        "title_dense": dense,
        "title_sparse": sparse
    }