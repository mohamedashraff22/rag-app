from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId


class DataChunk(BaseModel):
    # _id: Optional[ObjectId] # problem of _id -> as underscore for the pydantic means this is private
    # None means that its not required (optional and if its not found put it None)
    id: Optional[ObjectId] = Field(None, alias="_id")
    # ... (elipsis) -> field is required
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)  # gt -> greater than 0
    chunk_project_id: ObjectId  # for making relationships

    class Config:
        arbitrary_types_allowed = True  # this will allow any strange types

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "chunk_project_id_index_1",
                "unique": False,  # False -> may be we input a duplicated chunk its ok.
            },
        ]
