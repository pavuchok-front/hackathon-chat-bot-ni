"""Модульные документы: поиск шаблона, извлечение данных из свободного текста, пошаговое заполнение."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.config import TEMPLATES_DIR
from app.services.nlp import stem, tokens

MONTHS = {"января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6, "июля": 7, "августа": 8,
          "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12}
SEP = r"\s*[—:\-–=]+\s*"


@dataclass
class Template:
    raw: dict

    @property
    def id(self): return self.raw["id"]
    @property
    def title(self): return self.raw["title"]
    @property
    def fields(self): return self.raw.get("fields", [])


def load_templates() -> list[Template]:
    return [Template(json.loads(p.read_text(encoding="utf-8"))) for p in sorted(TEMPLATES_DIR.glob("*.json"))]


def find_template(text: str, templates: list[Template]) -> Template | None:
    low = text.lower()
    best, best_len = None, 0
    for t in templates:
        for a in t.raw.get("aliases", []):
            if a in low and len(a) > best_len:
                best, best_len = t, len(a)
    return best


def norm_date(s: str) -> str:
    s = s.strip().rstrip(".")
    m = re.match(r"(\d{1,2})\s+([а-я]+)\s+(\d{4})", s.lower())
    if m and m.group(2) in MONTHS:
        return f"{int(m.group(1)):02d}.{MONTHS[m.group(2)]:02d}.{m.group(3)}"
    return s


def extract_values(t: Template, text: str) -> dict[str, str]:
    """Достаёт значения полей, которые пользователь уже назвал («руководитель — Иванов И.И., срок — 30 ноября 2026»).
    Ничего не выдумывает: если поле не названо явно, оно остаётся пустым и бот спросит."""
    out: dict[str, str] = {}
    def grab(pattern: str) -> str | None:
        m = re.search(pattern + SEP + r"([^,;\n]+)", text, re.I)
        return m.group(1).strip() if m else None
    if t.id == "working_group":
        if v := grab(r"руководител\w*"): out["leader"] = v
        if v := grab(r"секретар\w*"): out["secretary"] = v
        if v := grab(r"срок\w*"): out["deadline"] = norm_date(v)
        if v := grab(r"цел\w*"): out["goal"] = v
        if v := grab(r"результат\w*"): out["result"] = v
        m = re.search(r"готов(?:им|ится|ить|лю)\s+([^,;\n]+)", text, re.I)
        if m:
            out["topic"] = m.group(1).strip()
            out.setdefault("goal", "подготовить " + m.group(1).strip())
    else:
        for f in t.fields:
            key_word = f["label"].split()[-1][:6]
            if v := grab(re.escape(key_word) + r"\w*"):
                out[f["key"]] = norm_date(v) if "дата" in f["label"] else v
    return out


def missing(t: Template, values: dict, only_required: bool = True) -> list[dict]:
    return [f for f in t.fields if f["key"] not in values and (f["required"] or not only_required)]


def render(t: Template, values: dict) -> str:
    body = t.raw["body"]
    def sub(m):
        key = m.group(1)
        if key in values and values[key]:
            return values[key]
        label = next((f["label"] for f in t.fields if f["key"] == key), key)
        return f"[уточнить: {label}]"
    # необязательное краткое наименование: если не задано, используем полное
    if t.id == "is_commissioning" and not values.get("system_short"):
        values = {**values, "system_short": values.get("system_full", "")}
    return re.sub(r"\{(\w+)\}", sub, body)


def blank(t: Template) -> str:
    return re.sub(r"\{(\w+)\}", lambda m: "[" + next((f["label"] for f in t.fields if f["key"] == m.group(1)), m.group(1)) + "]", t.raw["body"])
