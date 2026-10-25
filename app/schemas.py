"""Pydantic-модели. Старые поля (answer, sources, needs_clarification, clarifying_question) сохранены для совместимости с фронтом."""
from pydantic import BaseModel, Field


class SourceSchema(BaseModel):
    document: str
    section: str
    chunk_id: str = ""
    version: str = ""
    relevance: float | None = None


class ChatRequestSchema(BaseModel):
    message: str = Field(min_length=2, max_length=4000)
    session_id: str | None = None
    ai_mode: bool = False


class ChatResponseSchema(BaseModel):
    answer: str
    sources: list[SourceSchema] = Field(default_factory=list)
    needs_clarification: bool = False
    clarifying_question: str | None = None
    status: str = "answered"          # answered | clarification | refusal | template | draft | check
    session_id: str
    draft: str | None = None          # черновик документа (отдельно от текста ответа)
    suggestions: list[str] = Field(default_factory=list)
    mode: str = "rules"               # llm | extractive | rules
    relevance: float | None = None


class UploadResponseSchema(BaseModel):
    document_id: str
    filename: str
    status: str
    session_id: str
    chars: int
