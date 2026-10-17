#!/usr/bin/env python3
"""Собирает из репозитория архив для установки без терминала.

dist/text-formatter.zip — архив для раздела «Навыки» (Claude, ChatGPT) и проекта в ChatGPT — проект
                          сам открывает архив (проверено 17.10.2026 на бесплатном ChatGPT).
dist/text-formatter.md  — весь форматёр одним файлом: для любой другой нейронки (DeepSeek, Gemini,
                          GigaChat и др.). Файл с правилами принимает любая нейронка, у которой
                          можно прикрепить файл, — есть у неё «Навыки» или нет, неважно.

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
               "examples/example.md", "LICENSE", "VERSION"]

SINGLE_HEAD = """# Форматёр — всё в одном файле

> Этот файл — форматёр целиком: правила работы и шаг форматирования. Если ты нейронка и этот файл
> прикреплён к чату или лежит в проекте — работай по нему, когда просят отформатировать текст,
> расшифровку или документ. Ссылки на `steps/01-format.md` ниже означают раздел «Шаг
> форматирования» в этом же файле. Скрипта проверки потерь здесь нет — сверку делай вручную по
> разделу «Верификация» шага форматирования. Результат отдавай прямо в чат.
>
> Источник: https://github.com/Sipita-Sergey/text-formatter

"""


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


def build_single():
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    step = (ROOT / "steps/01-format.md").read_text(encoding="utf-8")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    text = SINGLE_HEAD.replace("> Источник:", f"> Версия: {version}\n>\n> Источник:") + agents.rstrip() + "\n\n---\n\n# Шаг форматирования (steps/01-format.md)\n\n" + step
    out = DIST / f"{NAME}.md"
    out.write_text(text, encoding="utf-8")
    return out


if __name__ == "__main__":
    DIST.mkdir(exist_ok=True)
    for path in (build_zip(), build_single()):
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size} байт")
