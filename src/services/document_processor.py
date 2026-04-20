"""Document processing service for handling various file types."""

from pathlib import Path
from typing import List, Optional
import hashlib
from dataclasses import dataclass, field

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import settings
from src.core.logging import logger


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""
    page_content: str
    metadata: dict = field(default_factory=dict)


class DocumentProcessor:
    """Process and chunk documents for RAG pipeline."""

    SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

    def _generate_doc_id(self, content: str) -> str:
        """Generate unique document ID based on content hash."""
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _load_pdf(self, file_path: Path) -> str:
        """Load text from PDF."""
        from pypdf import PdfReader

        reader = PdfReader(str(file_path))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def _load_text(self, file_path: Path) -> str:
        """Load text from TXT/MD file."""
        return file_path.read_text(encoding="utf-8")

    def load_document(self, file_path: str) -> str:
        """Load a document and return its text content."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {extension}")

        logger.info(f"Loading document: {path.name}")

        if extension == ".pdf":
            text = self._load_pdf(path)
        else:
            text = self._load_text(path)

        logger.info(f"Loaded document: {path.name} ({len(text)} chars)")
        return text

    def process_document(
        self,
        file_path: str,
        metadata: Optional[dict] = None,
    ) -> List[DocumentChunk]:
        """Load and chunk a document."""
        text = self.load_document(file_path)
        base_metadata = metadata or {}
        base_metadata["source_file"] = Path(file_path).name

        return self._split_text(text, base_metadata)

    def process_text(
        self,
        text: str,
        metadata: Optional[dict] = None,
    ) -> List[DocumentChunk]:
        """Process raw text into chunks."""
        base_metadata = metadata or {}
        return self._split_text(text, base_metadata)

    def _split_text(
        self,
        text: str,
        base_metadata: dict,
    ) -> List[DocumentChunk]:
        """Split text into chunks with metadata."""
        texts = self.text_splitter.split_text(text)

        chunks = []
        for i, chunk_text in enumerate(texts):
            chunk_metadata = {
                **base_metadata,
                "chunk_id": i,
                "doc_id": self._generate_doc_id(chunk_text[:100]),
            }
            chunks.append(
                DocumentChunk(
                    page_content=chunk_text,
                    metadata=chunk_metadata,
                )
            )

        logger.info(f"Created {len(chunks)} chunks")
        return chunks