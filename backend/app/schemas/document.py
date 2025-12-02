"""Document schemas for API request/response."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """Schema for document response."""

    id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    """Schema for paginated document list response."""

    items: list[DocumentResponse]
    total: int
    page: int
    per_page: int
    pages: int


class ChunkSummary(BaseModel):
    """Summary of document chunks."""

    id: uuid.UUID
    chunk_index: int
    content_preview: str
    metadata: dict | None

    model_config = ConfigDict(from_attributes=True)


class DocumentDetailResponse(BaseModel):
    """Schema for document detail with chunks summary."""

    id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    chunks: list[ChunkSummary]

    model_config = ConfigDict(from_attributes=True)
