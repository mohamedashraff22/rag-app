from pydantic import BaseModel, Field, validator
from typing import Optional
from bason.objectid import ObjectId


class Project(BaseModel):
    # any document put in mongodb , _id is added automatically, and this is its type -> ObjectId
    _id: Optional[ObjectId]
    project_id: str = Field(..., min_length=1)

    # design custom validation
    # ex: project id should be only numbers or letters (alphanumeric) -> using vallidator
    @validator("project_id")
    def validate_project_id(
        cls, value
    ):  # cls -> class project , value -> value from user
        if not value.isalnum():  # isalnum -> is alpha numeric ?
            raise ValueError("Project ID should be alphanumeric")
        return value

    # Object_id is a strange type for pydantic , so we it cant validate it and it will give me an error.
    class config:
        arbitrary_types_allowed = True  # this will allow any strange types
