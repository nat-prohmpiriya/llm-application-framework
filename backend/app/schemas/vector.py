"""Vector store schemas for chunk operations."""

import uuid

from pydantic import BaseModel, ConfigDict, Field


class ChunkCreate(BaseModel):
    """Schema for creating a document chunk with embedding."""

    document_id: uuid.UUID
    content: str
    embedding: list[float]
    chunk_index: int
    metadata: dict | None = None


class ChunkResult(BaseModel):
    """Schema for chunk search results."""

    id: uuid.UUID
    document_id: uuid.UUID
    content: str
    chunk_index: int
    score: float = Field(description="Similarity score (cosine distance, lower is better)")
    metadata: dict | None = None

    model_config = ConfigDict(from_attributes=True)
