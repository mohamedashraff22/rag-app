"""
Process controller module for handling document loading and text splitting.
"""

from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from models import ProcessingEnum
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Document:
    """
    Data class representing a processed document chunk.
    """
    page_content: str
    metadata: dict


class ProcessController(BaseController):
    """
    Controller for processing files, including loading content and splitting into chunks.
    """

    def __init__(self, project_id: str):
        """
        Initializes the process controller for a specific project.
        """
        super().__init__()
        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str) -> str:
        """
        Retrieves the file extension from a file ID.
        """
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):
        """
        Returns the appropriate LangChain loader based on the file extension.
        
        Args:
            file_id (str): The ID/name of the file to load.
            
        Returns:
            Loader: A LangChain document loader or None if not supported.
        """
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(self.project_path, file_id)

        if not os.path.exists(file_path):
            return None

        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        return None

    def get_file_content(self, file_id: str) -> Optional[List]:
        """
        Loads the content of a file using the detected loader.
        """
        loader = self.get_file_loader(file_id=file_id)
        if loader:
            return loader.load()
        return None

    def process_file_content(
        self,
        file_content: list,
        file_id: str,
        chunk_size: int = 100,
        chunk_overlap: int = 20,
    ) -> List[Document]:
        """
        Processes raw file content into structured data chunks.
        
        Args:
            file_content (list): Content list from the loader.
            file_id (str): The ID of the file being processed.
            chunk_size (int): Target size for each chunk.
            chunk_overlap (int): Overlap between chunks (currently not used in simpler splitter).
            
        Returns:
            List[Document]: A list of Document objects containing chunked text.
        """
        file_content_texts = [rec.page_content for rec in file_content]
        file_content_metadata = [rec.metadata for rec in file_content]

        chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size,
        )
        return chunks

    def process_simpler_splitter(
        self, 
        texts: List[str], 
        metadatas: List[dict], 
        chunk_size: int, 
        splitter_tag: str = "\n"
    ) -> List[Document]:
        """
        An optimized text splitting strategy that groups lines into chunks of a target size.
        
        Args:
            texts (List[str]): List of texts to split.
            metadatas (List[dict]): List of metadata dictionaries.
            chunk_size (int): Minimum character size for each chunk.
            splitter_tag (str): Tag used for joining and splitting lines.
            
        Returns:
            List[Document]: A list of chunked Document objects.
        """
        full_text = " ".join(texts)

        # Split into lines and filter out empty ones
        lines = [doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))
                current_chunk = ""

        # Handle any remaining text
        if current_chunk.strip():
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={}
            ))

        return chunks