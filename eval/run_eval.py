"""Оценка качества на golden_set.json (он больше НЕ источник ответов, а тест).
Запуск: python -m eval.run_eval [--llm]   (по умолчанию LLM выключена — проверяется детерминированный режим)"""
import json
import os
import re
import sys

if "--llm" not in sys.argv:
    os.environ["LLM_ENABLED"] = "0"
sys.path.insert(0, ".")

from app.config import GOLDEN_SET_PATH
from app.services.dialog import DialogEngine
from app.services.kb import KnowledgeBase

engine = DialogEngine(KnowledgeBase())
cases = json.load(open(GOLDEN_SET_PATH, encoding="utf-8"))
ok_total = 0
for c in cases:
    r = engine.handle(None, c["query"])
    got = {s["chunk_id"] for s in r["sources"]}
    text = r["answer"] + (("\n" + r["draft"]) if r.get("draft") else "")
    fails = []
    if c["is_refusal"]:
        if r["status"] != "refusal" or r["sources"]:
            fails.append(f"ожидался отказ без источников, получено {r['status']}")
    else:
        need = set(c["retrieval_sufficient"])
        if c["type"] not in ("уточнение_недостаточно_контекста",) and not need <= got and not (need & got):
            fails.append(f"поиск: ожидали {sorted(need)}, нашли {sorted(got)}")
        if c["type"] == "уточнение_недостаточно_контекста" and r["status"] != "clarification":
            fails.append("ожидалось уточнение")
        if c["requires_citation"] and c["citation_format"] and not re.search(c["citation_format"], text):
            fails.append("нет ссылки нужного формата")
    if c["type"] == "заполнение_шаблона" and not all(x in (r.get("draft") or "") for x in ("Иванов И.И.", "Петрова А.С.", "30.11.2026")):
        fails.append("черновик не содержит названных значений")
    low = text.lower()
    for bad in c["forbidden_claims"]:
        if bad.lower() in low:
            fails.append(f"запрещённое утверждение: {bad}")
    ok_total += not fails
    print(("OK  " if not fails else "FAIL"), c["id"], c["type"], "|", r["status"], "|", "; ".join(fails))
print(f"\nИтого: {ok_total}/{len(cases)}")
