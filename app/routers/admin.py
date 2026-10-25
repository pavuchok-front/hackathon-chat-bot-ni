"""Минимальная админка: загрузка материалов в RAG-базу без правки кода."""
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile

from app.config import ADMIN_TOKEN, ADMIN_UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
from app.deps import engine, kb

router = APIRouter(prefix="/api/admin", tags=["Администрирование"])


def _auth(token: str | None) -> None:
    if not token or token != ADMIN_TOKEN:
        raise HTTPException(401, "Неверный токен администратора")


@router.get("/kb")
def kb_info(x_admin_token: str | None = Header(default=None)):
    _auth(x_admin_token)
    return kb.info()


@router.post("/upload")
async def upload_knowledge_file(file: UploadFile = File(...), x_admin_token: str | None = Header(default=None)):
    _auth(x_admin_token)
    name = Path(file.filename or "").name
    ext = Path(name).suffix.lower()
    if not name or ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Разрешены PDF, DOCX, TXT и MD")
    data = await file.read()
    if not data or len(data) > MAX_FILE_SIZE:
        raise HTTPException(400, "Файл пустой или превышает 10 МБ")
    ADMIN_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target = ADMIN_UPLOAD_DIR / f"{uuid4().hex}_{name}"
    target.write_bytes(data)
    count = kb.reload()
    engine.templates = engine.templates  # Явно сохраняем активные шаблоны: догрузка меняет только базу.
    return {"status": "uploaded", "filename": name, "chunks": count}


@router.post("/reload")
def reload_knowledge(x_admin_token: str | None = Header(default=None)):
    _auth(x_admin_token)
    return {"chunks": kb.reload()}
