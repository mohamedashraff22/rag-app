"""
NLP controller module for handling vector database operations, embedding, and RAG logic.
"""

from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List, Tuple, Optional
import json


class NLPController(BaseController):
    """
    Controller for managing NLP-related operations, including interaction with
    VectorDB, LLMs, and template parsing for RAG.
    """

    def __init__(self, vectordb_client, generation_client, 
                 embedding_client, template_parser):
        """
        Initializes the NLP controller with necessary clients and parsers.
        """
        super().__init__()
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str) -> str:
        """
        Generates a consistent collection name for a project in the vector database.
        """
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip()
    
    async def reset_vector_db_collection(self, project: Project):
        """
        Deletes the vector database collection associated with a project.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)
        return await self.vectordb_client.delete_collection(collection_name=collection_name)
    
    async def get_vector_db_collection_info(self, project: Project) -> dict:
        """
        Retrieves detailed information about a project's vector database collection.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)

        # Convert complex objects to JSON-serializable dictionary
        return json.loads(
            json.dumps(collection_info, default=lambda x: getattr(x, '__dict__', str(x)))
        )
    
    async def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                                   chunks_ids: List[int], 
                                   do_reset: bool = False) -> bool:
        """
        Embeds and indexes data chunks into the vector database.
        
        Args:
            project (Project): The project context.
            chunks (List[DataChunk]): List of data chunks to index.
            chunks_ids (List[int]): List of database IDs for the chunks.
            do_reset (bool): Whether to reset the collection before indexing.
            
        Returns:
            bool: True if indexing was successful.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)

        texts = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        
        # Batch embedding of texts
        vectors = self.embedding_client.embed_text(
            text=texts, 
            document_type=DocumentTypeEnum.DOCUMENT.value
        )

        # Ensure collection exists
        await self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # Perform batch insertion
        await self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True

    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        """
        Performs a semantic search in the project's vector database collection.
        
        Args:
            project (Project): The project context.
            text (str): The search query text.
            limit (int): Maximum number of results to return.
            
        Returns:
            List or bool: List of search results or False if search failed.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)

        # Generate embedding for the query
        vectors = self.embedding_client.embed_text(
            text=text, 
            document_type=DocumentTypeEnum.QUERY.value
        )

        if not vectors:
            return False
        
        query_vector = vectors[0] if isinstance(vectors, list) and vectors else None

        if not query_vector:
            return False    

        # Execute semantic search
        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit
        )

        return results if results else False
    
    async def answer_rag_question(self, project: Project, query: str, limit: int = 10) -> Tuple[Optional[str], Optional[str], Optional[list]]:
        """
        Generates an answer to a question using the Retrieval-Augmented Generation (RAG) pipeline.
        
        Args:
            project (Project): The project context.
            query (str): The user's question.
            limit (int): Number of documents to retrieve for context.
            
        Returns:
            Tuple: (answer, full_prompt, chat_history)
        """
        answer, full_prompt, chat_history = None, None, None

        # Step 1: Retrieve relevant documents
        retrieved_documents = await self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_documents:
            return answer, full_prompt, chat_history
        
        # Step 2: Construct the LLM prompt using templates
        system_prompt = self.template_parser.get("rag", "system_prompt")

        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                "doc_num": idx + 1,
                "chunk_text": self.generation_client.process_text(doc.text),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt", {"query": query})

        # Step 3: Prepare the generation context
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([documents_prompts, footer_prompt])

        # Step 4: Generate the answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history