"""
Qdrant database provider module for handling vector storage and semantic search.
This module integrates with the Qdrant vector database.
"""

from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List, Optional, Any
from models.db_schemes import RetrievedDocument


class QdrantDBProvider(VectorDBInterface):
    """
    Provider implementation for Qdrant vector database.
    """

    def __init__(
        self, 
        db_client: str, 
        default_vector_size: int = 786,
        distance_method: Optional[str] = None, 
        index_threshold: int = 100
    ):
        """
        Initializes the Qdrant provider.
        
        Args:
            db_client (str): Connection path or URL for Qdrant.
            default_vector_size (int): Default dimension size for vectors.
            distance_method (Optional[str]): Distance metric (COSINE or DOT).
            index_threshold (int): Threshold for indexing optimization.
        """
        self.client = None
        self.db_client = db_client
        self.distance_method = None
        self.default_vector_size = default_vector_size

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger('uvicorn')

    async def connect(self):
        """
        Establishes a connection to the Qdrant client.
        """
        self.client = QdrantClient(path=self.db_client)

    async def disconnect(self):
        """
        Closes the connection to the Qdrant client.
        """
        self.client = None

    async def is_collection_existed(self, collection_name: str) -> bool:
        """
        Checks if a specific collection exists in the vector database.
        """
        return self.client.collection_exists(collection_name=collection_name)
    
    async def list_all_collections(self) -> List:
        """
        Lists all available collections in the database.
        """
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        """
        Retrieves metadata and statistics for a specific collection.
        """
        return self.client.get_collection(collection_name=collection_name)
    
    async def delete_collection(self, collection_name: str):
        """
        Deletes a collection from the database if it exists.
        """
        if await self.is_collection_existed(collection_name):
            self.logger.info(f"Deleting collection: {collection_name}")
            return self.client.delete_collection(collection_name=collection_name)
        
    async def create_collection(
        self, 
        collection_name: str, 
        embedding_size: int,
        do_reset: bool = False
    ) -> bool:
        """
        Creates a new collection in the database.
        
        Args:
            collection_name (str): Name of the collection.
            embedding_size (int): Dimension of the embedding vectors.
            do_reset (bool): If True, delete existing collection first.
            
        Returns:
            bool: True if created, False otherwise.
        """
        if do_reset:
            await self.delete_collection(collection_name=collection_name)
        
        if not await self.is_collection_existed(collection_name):
            self.logger.info(f"Creating new Qdrant collection: {collection_name}")
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            return True
        
        return False
    
    async def insert_one(
        self, 
        collection_name: str, 
        text: str, 
        vector: list,
        metadata: Optional[dict] = None, 
        record_id: Optional[Any] = None
    ) -> bool:
        """
        Inserts a single record into the specified collection.
        """
        if not await self.is_collection_existed(collection_name):
            self.logger.error(f"Cannot insert into non-existent collection: {collection_name}")
            return False
        
        try:
            self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text, "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error during single record insertion: {e}")
            return False

        return True
    
    async def insert_many(
        self, 
        collection_name: str, 
        texts: list, 
        vectors: list, 
        metadata: Optional[list] = None, 
        record_ids: Optional[list] = None, 
        batch_size: int = 50
    ) -> bool:
        """
        Inserts multiple records into the specified collection in batches.
        """
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            batch_records = [
                models.Record(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x], "metadata": batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]

            try:
                self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error during batch insertion: {e}")
                return False

        return True
        
    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5) -> Optional[List[RetrievedDocument]]:
        """
        Searches the collection using a query vector.
        
        Args:
            collection_name (str): The collection to search.
            vector (list): The query embedding vector.
            limit (int): Number of results to return.
            
        Returns:
            Optional[List[RetrievedDocument]]: List of retrieved documents or None.
        """
        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        if not results:
            return None
        
        return [
            RetrievedDocument(**{
                "score": result.score,
                "text": result.payload["text"],
            })
            for result in results
        ]