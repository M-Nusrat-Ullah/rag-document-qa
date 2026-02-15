"""Document processing service for handling various file types."""

from pathlib import Path
from typing import List, Optional
import hashlib

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
)
from langchain_core.documents import Document

from src.core.config import settings
from src.core.logging import logger


class DocumentProcessor:
    """Process and chunk documents for RAG pipeline."""
    
    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".docx", ".md"}
    
    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def _get_loader(self, file_path: Path):
        """Get appropriate loader based on file extension."""
        extension = file_path.suffix.lower()
        
        loaders = {
            ".pdf": PyPDFLoader,
            ".txt": TextLoader,
            ".md": TextLoader,
            ".docx": Docx2txtLoader,
        }
        
        loader_class = loaders.get(extension)
        if not loader_class:
            raise ValueError(f"Unsupported file type: {extension}")
        
        return loader_class(str(file_path))
    
    def _generate_doc_id(self, content: str) -> str:
        """Generate unique document ID based on content hash."""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def load_document(self, file_path: str) -> List[Document]:
        """Load a document from file path."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        logger.info(f"Loading document: {path.name}")
        
        loader = self._get_loader(path)
        documents = loader.load()
        
        logger.info(f"Loaded {len(documents)} pages from {path.name}")
        return documents
    
    def process_document(
        self,
        file_path: str,
        metadata: Optional[dict] = None
    ) -> List[Document]:
        """Load and chunk a document."""
        
        # Load document
        documents = self.load_document(file_path)
        
        # Add custom metadata
        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add chunk-specific metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["doc_id"] = self._generate_doc_id(
                chunk.page_content[:100]
            )
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def process_text(
        self,
        text: str,
        metadata: Optional[dict] = None
    ) -> List[Document]:
        """Process raw text into chunks."""
        
        doc = Document(
            page_content=text,
            metadata=metadata or {}
        )
        
        chunks = self.text_splitter.split_documents([doc])
        
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
            chunk.metadata["doc_id"] = self._generate_doc_id(
                chunk.page_content[:100]
            )
        
        return chunks