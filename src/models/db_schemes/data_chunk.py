from pydantic import BaseModel, Field, validator
from typing import Optional
from bason.objectid import ObjectId


class DataChunk(BaseModel):
    _id: Optional[ObjectId]
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)  # gt -> greater than 0
    chunk_project_id: ObjectId  # for making relationships

    class config:
        arbitrary_types_allowed = True  # this will allow any strange types
