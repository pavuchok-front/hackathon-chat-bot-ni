"""Настройки. Всё переопределяется переменными окружения."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
KB_DIR = Path(os.getenv("KB_DIR", BASE_DIR / "knowledge_base"))
TEMPLATES_DIR = BASE_DIR / "templates"
UPLOAD_DIR = BASE_DIR / "uploads"
GOLDEN_SET_PATH = BASE_DIR / "golden_set.json"   # используется ТОЛЬКО для оценки качества (eval/run_eval.py)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024

# Администрирование. В production значение обязательно задаётся через секреты окружения.
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "demo-admin-change-me")
ADMIN_UPLOAD_DIR = KB_DIR / "admin_uploads"

# Локальная open-source LLM через Ollama. Данные не покидают контур.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
LLM_ENABLED = os.getenv("LLM_ENABLED", "1") == "1"

# Облачный режим через OpenRouter с Qwen 2.5. Ключ хранится только на сервере.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-72b-instruct")

# Пороги релевантности (доля «веса» слов запроса, найденных в положении)
ANSWER_THRESHOLD = float(os.getenv("ANSWER_THRESHOLD", "0.45"))
WEAK_THRESHOLD = float(os.getenv("WEAK_THRESHOLD", "0.35"))

# Ролевая модель: какие уровни доступа видит роль
ROLES = {"employee": {"public"}, "doc_expert": {"public", "restricted"}}
DEFAULT_ROLE = "employee"
SESSION_TTL_SEC = 3600
