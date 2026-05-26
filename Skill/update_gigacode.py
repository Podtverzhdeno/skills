"""
update_gigacode.py — Используется на каждом шаге аудита.

Безопасно добавляет или заменяет секцию в gigacode.md.
Никогда не перезаписывает файл целиком — только нужную секцию.

Использование:
    # Добавить/обновить секцию (контент из аргумента):
    python scripts/update_gigacode.py <gigacode_path> <section_title> --content "текст секции"

    # Добавить/обновить секцию (контент из stdin):
    echo "текст" | python scripts/update_gigacode.py <gigacode_path> <section_title>

    # Добавить/обновить секцию (контент из файла):
    python scripts/update_gigacode.py <gigacode_path> <section_title> --file /tmp/section.txt

Примеры:
    python scripts/update_gigacode.py gigacode.md "[ШАГ 1] Архитектура" --content "..."
    python scripts/update_gigacode.py gigacode.md "[ШАГ 3] POST /api/orders" --file /tmp/orders.md

Вывод: JSON с результатом операции
"""

import sys
import json
import argparse
import re
from pathlib import Path


# ─── Утилиты ─────────────────────────────────────────────────────────────────

GIGACODE_HEADER = "# GigaCode — Архитектурный анализ и аудит API\n\n"

SECTION_LEVEL = "##"  # все секции второго уровня


def make_section(title: str, content: str) -> str:
    """Формирует markdown-секцию."""
    content = content.strip()
    return f"{SECTION_LEVEL} {title}\n\n{content}\n"


def section_pattern(title: str) -> re.Pattern:
    """Регулярка для поиска существующей секции с таким заголовком."""
    escaped = re.escape(title)
    # Секция — от ## Title до следующего ## или конца файла
    return re.compile(
        rf"^{re.escape(SECTION_LEVEL)}\s+{escaped}\s*\n.*?(?=^{re.escape(SECTION_LEVEL)}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )


def read_gigacode(path: Path) -> str:
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return ""
    return ""


def write_gigacode(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ─── Основная логика ─────────────────────────────────────────────────────────

def update(gigacode_path: str, section_title: str, content: str) -> dict:
    path = Path(gigacode_path)
    existing = read_gigacode(path)

    new_section = make_section(section_title, content)
    pat = section_pattern(section_title)

    if not existing:
        # Файл не существует — создаём с нуля
        result_content = GIGACODE_HEADER + new_section
        write_gigacode(path, result_content)
        return {
            "status": "created",
            "file": str(path),
            "section": section_title,
            "message": f"Файл создан, секция '{section_title}' добавлена.",
        }

    if pat.search(existing):
        # Секция уже есть — заменяем
        updated = pat.sub(new_section, existing)
        # Убедимся, что файл не закончился без новой строки
        if not updated.endswith("\n"):
            updated += "\n"
        write_gigacode(path, updated)
        return {
            "status": "updated",
            "file": str(path),
            "section": section_title,
            "message": f"Секция '{section_title}' обновлена.",
        }
    else:
        # Секции нет — добавляем в конец
        separator = "\n" if existing.endswith("\n") else "\n\n"
        updated = existing + separator + new_section
        write_gigacode(path, updated)
        return {
            "status": "appended",
            "file": str(path),
            "section": section_title,
            "message": f"Секция '{section_title}' добавлена в конец файла.",
        }


# ─── Точка входа ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Безопасно обновляет секцию в gigacode.md")
    parser.add_argument("gigacode_path", help="Путь к gigacode.md (будет создан если не существует)")
    parser.add_argument("section_title", help="Заголовок секции, например '[ШАГ 1] Архитектура'")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--content", help="Контент секции как строка")
    group.add_argument("--file", help="Путь к файлу с контентом секции")

    args = parser.parse_args()

    # Получаем контент
    if args.content:
        content = args.content
    elif args.file:
        try:
            content = Path(args.file).read_text(encoding="utf-8")
        except Exception as e:
            print(json.dumps({"error": f"Не удалось прочитать файл: {e}"}))
            sys.exit(1)
    else:
        # Читаем из stdin
        content = sys.stdin.read()

    if not content.strip():
        print(json.dumps({"error": "Контент секции пустой"}))
        sys.exit(1)

    result = update(args.gigacode_path, args.section_title, content)
    print(json.dumps(result, ensure_ascii=False, indent=2))
