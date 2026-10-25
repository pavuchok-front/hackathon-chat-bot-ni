"""Токенизация, простой русский стемминг, стоп-слова, синонимы аббревиатур."""
import re

TOKEN_RE = re.compile(r"[а-яёa-z0-9]+", re.IGNORECASE)

SUFFIXES = sorted([
    "ами", "ями", "ого", "его", "ому", "ему", "ыми", "ими", "ая", "яя", "ое", "ее", "ые", "ие", "ой", "ей",
    "ый", "ий", "ым", "им", "ов", "ев", "ам", "ям", "ах", "ях", "ом", "ем", "ую", "юю", "ать", "ять", "ить",
    "еть", "уть", "ыть", "ают", "яют", "уют", "ает", "яет", "ует", "ишь", "ешь", "ите", "ете", "ат", "ят",
    "ут", "ют", "ит", "ет", "ла", "ло", "ли", "ть", "ся", "сь", "а", "я", "ы", "и", "у", "ю", "о", "е", "ь",
], key=len, reverse=True)

STOP = set("""как что кто какой какая какие какое каких чем чего надо нужно нужны нужен ли мне мой моего мою мои
можно нельзя это этот эта эти для при про или если то же бы был была были быть есть нет не да но и в на по с со к у о об
от до за из над под после перед между через сколько когда где куда почему зачем ещё еще уже мы вы я он она они
дай дайте подскажи подскажите скажи скажите пожалуйста нужна хочу хотим необходимо должен должна должны
сделать сделай значит значение означает грозит считается""".split())

# аббревиатура -> расширение (стемы добавляются в запрос)
SYNONYMS = {
    "иб": "информационн безопасност", "дит": "информационн технологи", "ис": "информационн систем",
    "кадры": "кадров", "кадр": "кадров", "юристы": "юридическ юрист", "юрист": "юридическ",
    "дмс": "международн сотрудничеств", "доу": "доу документационн",
    "сп": "сп", "иис": "иис", "виза": "виз визирован", "визы": "виз визирован",
}


def stem(word: str) -> str:
    for suf in SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[: -len(suf)]
    return word


def tokens(text: str) -> list[str]:
    return [m.group(0) for m in TOKEN_RE.finditer(text.lower()) if len(m.group(0)) >= 2 and not m.group(0).isdigit()]


def stems_match(a: str, b: str) -> bool:
    if a == b:
        return True
    return len(a) >= 3 and len(b) >= 3 and (a.startswith(b) or b.startswith(a))


def content_stems(text: str, expand: bool = True) -> list[str]:
    out: list[str] = []
    for tok in tokens(text):
        if tok in STOP:
            continue
        out.append(stem(tok))
        if expand and tok in SYNONYMS:
            out.extend(stem(w) if len(w) > 3 else w for w in SYNONYMS[tok].split())
    seen, uniq = set(), []
    for s in out:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq
