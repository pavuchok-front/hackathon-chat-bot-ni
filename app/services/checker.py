"""Проверка проекта документа: детерминированные правила + привязка замечаний к положениям базы знаний."""
import re
from datetime import date

DATE_RE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
PLACEHOLDERS = [
    (re.compile(r"\[[^\]\n]{0,60}\]"), "незаполненное поле в квадратных скобках"),
    (re.compile(r"_{3,}"), "незаполненное поле (подчёркивания)"),
    (re.compile(r"\{[^}\n]{1,40}\}"), "неподставленный параметр шаблона {…}"),
    (re.compile(r"<[^>\n]{1,40}>"), "служебный элемент шаблона <…>"),
    (re.compile(r"\b(ДД\.ММ\.ГГГГ|XX\.XX\.XXXX|уточнить)\b", re.I), "заглушка вместо значения"),
]
TEMPLATE_LEFTOVERS = [
    (re.compile(r"^\s*Примечание: проект подготовлен по модулю.*$", re.M), "служебное примечание шаблона нужно удалить перед визированием"),
    (re.compile(r"^\s*(Пояснени[ея]\s*\d*[:.].*)$", re.M | re.I), "пояснение к модулю не должно оставаться в тексте проекта"),
]


def _d(m) -> date | None:
    try:
        return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None


def check_text(text: str) -> list[dict]:
    findings: list[dict] = []

    for rx, why in PLACEHOLDERS:
        found = sorted(set(m.group(0) for m in rx.finditer(text)))
        if found:
            findings.append({"severity": "error", "message": f"Есть {why}: {', '.join(found[:5])}. Заполните или удалите.", "chunk": None})

    for rx, why in TEMPLATE_LEFTOVERS:
        if rx.search(text):
            findings.append({"severity": "warn", "message": f"Лишний элемент шаблона: {why}.", "chunk": None})

    # единообразие наименований: все слова в кавычках, различающиеся только регистром
    quoted = re.findall(r"[«\"'“]([^»\"'”\n]{2,60})[»\"'”]", text)
    groups: dict[str, set[str]] = {}
    for q in quoted:
        groups.setdefault(q.strip().lower(), set()).add(q.strip())
    for variants in groups.values():
        if len(variants) > 1:
            findings.append({"severity": "error", "chunk": "mod_is_02",
                             "message": f"Наименование пишется по-разному: {' / '.join('«'+v+'»' for v in sorted(variants))}. "
                                        "Оно должно быть одинаковым во всех пунктах (пояснение 4 к модулю)."})

    # дата ввода не раньше документа о готовности
    low = text.lower()
    intro = re.search(r"(?:дат\w*\s+ввода|ввод\w*[^.\n]{0,40}?)[^0-9\n]{0,30}(\d{2}\.\d{2}\.\d{4})", low)
    ready = re.search(r"(?:протокол\w*|акт\w*|готовност\w*)[^0-9\n]{0,60}(\d{2}\.\d{2}\.\d{4})", low)
    if intro and ready:
        d_in, d_rd = _d(DATE_RE.search(intro.group(1))), _d(DATE_RE.search(ready.group(1)))
        if d_in and d_rd and d_in < d_rd:
            findings.append({"severity": "error", "chunk": "mod_is_03",
                             "message": f"Дата ввода ({intro.group(1)}) раньше даты документа о готовности ({ready.group(1)}). "
                                        "Так нельзя, если не предусмотрен особый порядок (пояснение 8). Перенесите дату ввода или проверьте дату документа."})
    return findings
