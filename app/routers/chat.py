from fastapi import APIRouter, Header

from app.config import DEFAULT_ROLE, OPENROUTER_API_KEY, ROLES
from app.deps import engine, kb
from app.schemas import ChatRequestSchema, ChatResponseSchema
from app.services import llm

router = APIRouter(prefix="/api", tags=["Чат"])


@router.post("/chat", response_model=ChatResponseSchema, summary="Задать вопрос ассистенту")
def chat(payload: ChatRequestSchema, x_role: str = Header(default=DEFAULT_ROLE)) -> ChatResponseSchema:
    role = x_role if x_role in ROLES else DEFAULT_ROLE      # роль в проде приходит из SSO/прокси портала
    return ChatResponseSchema(**engine.handle(payload.session_id, payload.message, role, payload.ai_mode))


@router.get("/health", summary="Состояние: база знаний и LLM")
def health():
    return {"kb": kb.info(), "llm_available": llm.available(), "cloud_configured": bool(OPENROUTER_API_KEY)}


@router.post("/kb/reload", summary="Перечитать базу знаний (после добавления/обновления документов)")
def reload_kb(x_role: str = Header(default=DEFAULT_ROLE)):
    from fastapi import HTTPException
    if x_role != "doc_expert":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return {"chunks": kb.reload()}
