#!/usr/bin/env python3
"""Проверка форматирования на потерю содержания.

Сравнивает `<имя>.md` и `<имя>_formatted.md`: ищет содержательные слова, которые были
в исходнике и полностью исчезли в результате. Считает по корням и приводит «ё» к «е» —
иначе «удалённо» и «удаленно» читаются как разные слова, а переформулировка
(«рекрутить» → «рекрутировать») выглядит потерей.

    python3 check-losses.py <файл_formatted.md | папка>

(в Windows вместо `python3` — `python`)

Что скрипт НЕ умеет и почему это нормально: он не отличает законно вычищенное от
потерянного. Слово-паразит («понимаешь», «собственно») и починенное искажение
распознавания («корджобы» → Core Job) он покажет так же, как пропавшую мысль. Его дело —
сузить проверку с тысяч слов до десятков, которые человек или агент открывает в исходнике
по контексту и решает сам.

Grep для этой сверки не годится: на длинных кириллических шаблонах он молча возвращает
пустоту вместо ошибки, и потеря читается как «всё на месте».
"""
import re
import sys
from collections import Counter
from pathlib import Path

# служебная разметка расшифровки: [12:34] Спикер 0:
MARK = re.compile(r"\[\d+:\d+\]\s*Спикер \d+:")
NORM = re.compile(r"[^а-яa-z0-9 ]")
# разговорная шелуха и служебное — их исчезновение ожидаемо
NOISE = {
    "понимаешь", "собственно", "соответственно", "получается", "например", "наверное",
    "допустим", "условно", "короче", "смотрите", "смотришь", "посмотрим", "следующий",
    "следующее", "следующая", "пожалуйста", "микрофон", "слайдов", "слайде", "кликер",
    "секундочку", "минуточку", "действительно", "естественно", "получится", "сделаешь",
}

def words(text):
    return NORM.sub(" ", MARK.sub(" ", text).lower().replace("ё", "е")).split()

def find_source(out_path: Path):
    base = out_path.name[: -len("_formatted.md")]
    for ext in (".md", ".txt"):
        cand = out_path.with_name(base + ext)
        if cand.exists():
            return cand
    return None

def check(out_path: Path, min_len=8):
    src_path = find_source(out_path)
    if src_path is None:
        return None
    src = Counter(words(src_path.read_text(encoding="utf-8")))
    out = Counter(words(out_path.read_text(encoding="utf-8")))
    lost = {w: c for w, c in src.items()
            if len(w) >= min_len and out.get(w, 0) == 0 and w not in NOISE}
    sw, ow = sum(src.values()), sum(out.values())
    return sw, ow, lost

def main():
    # консоль Windows по умолчанию не в UTF-8: без этого галочка и кириллица роняют скрипт
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    target = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    files = [target] if target.is_file() else sorted(target.rglob("*_formatted.md"))
    if not files:
        print("не нашёл ни одного *_formatted.md"); return
    for f in files:
        r = check(f)
        if r is None:
            print(f"⚠ нет исходника рядом: {f.name}"); continue
        sw, ow, lost = r
        delta = (ow - sw) / sw * 100 if sw else 0
        head = f"{f.name[:52]:<52} {sw:>6} → {ow:>6} слов ({delta:+.0f}%)"
        if not lost:
            print(f"✓ {head}"); continue
        print(f"  {head}   проверить слов: {len(lost)}")
        for w, c in sorted(lost.items(), key=lambda x: -x[1])[:12]:
            print(f"      {w} ×{c}")

if __name__ == "__main__":
    main()
