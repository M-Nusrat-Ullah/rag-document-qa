"""Vector store service using ChromaDB."""

from typing import List, Optional, Dict, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain.schema import Document

from src.core.config import settings
from src.core.logging import logger
from src.services.embedding_service import get_embedding_service


class VectorStoreService:
    """Service for managing vector store operations."""
    
    def __init__(
        self,
        persist_directory: str = settings.chroma_persist_directory,
        collection_name: str = settings.collection_name
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Ensure directory exists
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize embedding service
        self.embedding_service = get_embedding_service()
        
        logger.info(f"Vector store initialized. Documents: {self.collection.count()}")
    
    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """Add documents to the vector store."""
        
        if not documents:
            return {"added": 0, "status": "no documents provided"}
        
        logger.info(f"Adding {len(documents)} documents to vector store")
        
        # Process in batches
        total_added = 0
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            # Extract texts and metadata
            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]
            ids = [f"{doc.metadata.get('doc_id', i)}_{doc.metadata.get('chunk_id', j)}" 
                   for j, doc in enumerate(batch, start=i)]
            
            # Generate embeddings
            embeddings = self.embedding_service.embed_texts(texts)
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            total_added += len(batch)
            logger.info(f"Added batch: {total_added}/{len(documents)}")
        
        return {
            "added": total_added,
            "total_documents": self.collection.count(),
            "status": "success"
        }
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        
        logger.info(f"Searching for: '{query[:50]}...' (k={k})")
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i],
                "relevance_score": 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        logger.info(f"Found {len(formatted_results)} results")
        return formatted_results
    
    def delete_collection(self) -> bool:
        """Delete the entire collection."""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            "collection_name": self.collection_name,
            "document_count": self.collection.count(),
            "persist_directory": self.persist_directory
        }