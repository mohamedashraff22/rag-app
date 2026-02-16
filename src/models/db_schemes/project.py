from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId


class Project(BaseModel):
    # any document put in mongodb , _id is added automatically, and this is its type -> ObjectId
    id: Optional[ObjectId] = Field(None, alias="_id")
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
    class Config:
        arbitrary_types_allowed = True  # this will allow any strange types

    # @ -> decorator (change the behaviour of a function)
    # self -> function from object (normal way), cls -> static funtion -> not from object of a class (cls instead of self is optional i can still use self, butused for more readability).
    @classmethod
    def get_indexes(cls):
        # return list of indecies.
        # we can use more than one key like use (chunk_order & and chunk_project_id as one key for search) but here we will jsut use one
        return [
            {
                "key": [  # one or more key (للفهرسة)
                    ("project_id", 1)  # 1 -> ascending , -1 descending
                ],
                "name": "project_id_index_1",  # just a name for this index, and it will not be used for any other index
                "unique": True,  # True -> in this filed all the values in it must be unique, and if i put a value that is already inside it give an error.
            },
        ]
