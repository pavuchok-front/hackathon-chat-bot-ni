"""ИИ-клиенты. Два режима:
- облако: Qwen 2.5 через OpenRouter (галочка «ИИ-режим» в интерфейсе). Ключ только на сервере.
- локально: Ollama (без галочки, если модель запущена). Данные не покидают контур.
Сбой не выбрасывает исключение наружу: возвращается LLMResult с описанием ошибки."""
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from app.config import (LLM_ENABLED, OLLAMA_MODEL, OLLAMA_URL, OPENROUTER_API_KEY,
                        OPENROUTER_BASE_URL, OPENROUTER_MODEL)


@dataclass
class LLMResult:
    text: str | None
    provider: str          # openrouter | ollama
    error: str = ""


_state = {"ok": False, "checked": 0.0}


def available() -> bool:
    """Локальная Ollama доступна (проверка раз в 30 секунд)."""
    if not LLM_ENABLED:
        return False
    if time.time() - _state["checked"] > 30:
        _state["checked"] = time.time()
        try:
            urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=1).read()
            _state["ok"] = True
        except Exception:
            _state["ok"] = False
    return _state["ok"]


def _messages(system: str, user: str) -> list[dict]:
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _post(url: str, body: dict, headers: dict, timeout: int) -> dict:
    req = urllib.request.Request(url, json.dumps(body).encode("utf-8"), headers)
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def _cloud(system: str, user: str, timeout: int, max_tokens: int = 700) -> LLMResult:
    if not OPENROUTER_API_KEY:
        return LLMResult(None, "openrouter", "OPENROUTER_API_KEY не задан в .env")
    body = {"model": OPENROUTER_MODEL, "temperature": 0.1, "max_tokens": max_tokens,
            "store": False, "messages": _messages(system, user)}
    headers = {"Content-Type": "application/json",
               "Authorization": f"Bearer {OPENROUTER_API_KEY}",
               "X-Title": "Reglament Assistant"}
    url = f"{OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"
    try:
        data = _post(url, body, headers, timeout)
        message = (data.get("choices") or [{}])[0].get("message") or {}
        text = (message.get("content") or "").strip()
        return LLMResult(text or None, "openrouter", "" if text else "пустой ответ модели")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        return LLMResult(None, "openrouter", f"HTTP {exc.code}: {detail}")
    except Exception as exc:
        return LLMResult(None, "openrouter", str(exc))


def _local(system: str, user: str, timeout: int) -> LLMResult:
    if not available():
        return LLMResult(None, "ollama", "Ollama не запущена")
    body = {"model": OLLAMA_MODEL, "stream": False, "options": {"temperature": 0.1},
            "messages": _messages(system, user)}
    try:
        data = _post(f"{OLLAMA_URL}/api/chat", body, {"Content-Type": "application/json"}, timeout)
        text = (data.get("message", {}).get("content") or "").strip()
        return LLMResult(text or None, "ollama", "" if text else "пустой ответ модели")
    except Exception as exc:
        _state["ok"] = False
        return LLMResult(None, "ollama", str(exc))


def generate(system: str, user: str, use_cloud: bool, timeout: int = 90, max_tokens: int = 700) -> LLMResult:
    """use_cloud=True — режим «ИИ» (Qwen 2.5 через OpenRouter); False — локальная модель, если запущена."""
    res = _cloud(system, user, timeout, max_tokens) if use_cloud else _local(system, user, timeout)
    if res.error:
        print(f"[llm:{res.provider}] {res.error}")   # подробности только в журнал сервера
    return res
