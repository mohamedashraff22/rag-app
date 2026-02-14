from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne


class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(
            chunk.dict(by_alias=True, exclude_unset=True)
        )
        chunk._id = result.inserted_id
        return chunk

    # in MongoDB we use "Object_id", outside mognodb we use "str"
    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one({"_id": ObjectId(chunk_id)})

        if result is None:
            return None

        return DataChunk(**result)  # unwrap this object to parameters of data chunk

    # we dont want to insert chunk (chunk by chunk) -> so we use "bulk write from motor" (for memory usage efficiency)
    # InsertOne is not insert_one
    # by default = 100 if i dont pass a value my self
    async def insert_many_chunks(self, chunks: list, batch_size: int = 100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            # for every batch
            operations = [
                # you can use insetmany instead of insert one -> sends the whole batch to memory (not efficient and causes problems)
                # we use InsertOne insstead of insert_one -> as here we only define the opertaions that will apply insert_one automatically onece we have the data
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)

        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        result = await self.collection.delete_many({"chunk_project_id": project_id})
        return result.deleted_count
