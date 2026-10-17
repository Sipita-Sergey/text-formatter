#!/usr/bin/env python3
"""Собирает из репозитория архив для установки без терминала.

dist/text-formatter.zip — один архив на все пути без терминала: раздел «Навыки» (Claude, ChatGPT)
                          и файлы проекта в ChatGPT без навыков — проект сам открывает архив
                          (проверено 17.10.2026 на бесплатном ChatGPT: отформатировал пример и
                          прогнал скрипт проверки потерь прямо из архива).

Зачем: руками поддерживается только репозиторий. Архив собирается из него заново при каждой
правке, поэтому расходиться с репозиторием ему не на чем.

Запуск: python3 tools/build-dist.py  (из корня репозитория)
"""
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
NAME = "text-formatter"

# Что входит в скилл. Инструкции установки и служебное для разработки в скилл не кладутся.
SKILL_FILES = ["SKILL.md", "AGENTS.md", "steps/01-format.md", "tools/check-losses.py",
               "examples/example.md", "LICENSE"]

def skill_md_for_upload():
    """SKILL.md для загрузки в «Навыки»: в шапке только name и description.

    Загрузка навыков проверяет шапку и может отвергнуть незнакомые ей поля (argument-hint нужен
    только Claude Code), поэтому в архив идёт шапка без них; тело файла — как в репозитории.
    """
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    _, head, body = text.split("---", 2)
    keep = [line for line in head.strip().splitlines() if line.split(":", 1)[0] in ("name", "description")]
    return "---\n" + "\n".join(keep) + "\n---" + body


def build_zip():
    out = DIST / f"{NAME}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in SKILL_FILES:
            if rel == "SKILL.md":
                z.writestr(f"{NAME}/SKILL.md", skill_md_for_upload())
            else:
                z.write(ROOT / rel, f"{NAME}/{rel}")
    return out


if __name__ == "__main__":
    DIST.mkdir(exist_ok=True)
    for path in (build_zip(),):
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size} байт")
