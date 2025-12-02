"""Embedding service using sentence-transformers."""

import logging
from typing import TYPE_CHECKING

from app.config import settings
from app.core.telemetry import traced

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""

    def __init__(self, model_name: str | None = None):
        """
        Initialize embedding service.

        Args:
            model_name: Model name to use (defaults to settings)
        """
        self.model_name = model_name or settings.embedding_model
        self._model: "SentenceTransformer | None" = None

    @property
    def model(self) -> "SentenceTransformer":
        """Lazy load model on first use."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model loaded: {self.model_name}")
        return self._model

    @traced()
    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed (for documents, use "passage: " prefix)

        Returns:
            Embedding vector as list of floats
        """
        # For e5 models, add "passage: " prefix for documents
        prefixed_text = f"passage: {text}"
        embedding = self.model.encode(prefixed_text, normalize_embeddings=True)
        return embedding.tolist()

    @traced()
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        # Add "passage: " prefix for e5 models
        prefixed_texts = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(prefixed_texts, normalize_embeddings=True)
        return embeddings.tolist()

    @traced()
    async def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for a search query.

        Args:
            query: Query text (will add "query: " prefix for e5 models)

        Returns:
            Embedding vector as list of floats
        """
        # For e5 models, add "query: " prefix for queries
        prefixed_query = f"query: {query}"
        embedding = self.model.encode(prefixed_query, normalize_embeddings=True)
        return embedding.tolist()

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()


# Singleton instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """
    Get embedding service singleton.

    Returns:
        EmbeddingService instance
    """
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService()

    return _embedding_service
