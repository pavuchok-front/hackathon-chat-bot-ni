"""Журнал аудита без текста вопросов и документов: только метаданные."""
import json
import time
from pathlib import Path

from app.config import BASE_DIR

LOG = BASE_DIR / "logs" / "audit.jsonl"


def log(session: str, role: str, status: str, chunk_ids: list[str]) -> None:
    try:
        LOG.parent.mkdir(exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": int(time.time()), "session": session[:8], "role": role, "status": status, "chunks": chunk_ids}, ensure_ascii=False) + "\n")
    except OSError:
        pass
