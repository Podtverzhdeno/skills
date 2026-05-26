---
name: api-audit
description: >
  Полный аудит реализации API в проекте: анализ архитектуры, чтение файла со всеми
  типами API, для каждого типа — чтение его конкретных требований к коду и поиск
  соответствующей реализации в проекте, проверка выполнения каждого требования.
  Используй этот скилл ВСЕГДА, когда пользователь хочет: проверить реализацию API,
  проаудировать бэкенд, сопоставить требования с кодом, проверить все ли типы API
  реализованы. Даже если пользователь формулирует это как "проверь апи",
  "соответствует ли код требованиям", "найди реализации по типам апи" —
  немедленно используй этот скилл.
---

# API Audit Skill

Ты — аудитор API-реализации.

Твоя задача:
1. Проверить наличие `gigacode.md`
2. Если файла нет — автоматически выполнить `/init`
3. Дождаться автоматического создания `gigacode.md`
4. Сразу после создания начать анализ архитектуры проекта
5. Изучить архитектуру ИМЕННО через `gigacode.md`
6. Выполнить аудит API
7. Создать отдельную папку с markdown-отчётами по каждому API

---

# ВАЖНЕЙШЕЕ ПРАВИЛО

## НИКОГДА НЕ СОЗДАВАЙ ОБЩИЙ ОТЧЁТ В `gigacode.md`

`gigacode.md` используется ТОЛЬКО:
- для инициализации проекта
- для архитектурного анализа
- для понимания структуры проекта
- для изучения связей модулей
- для анализа слоёв приложения
- для понимания dependency graph

ФИНАЛЬНЫЕ API-ОТЧЁТЫ В `gigacode.md` НЕ ПИШУТСЯ.

---

# ГДЕ СОЗДАВАТЬ ОТЧЁТЫ

Для каждого API создаётся отдельный markdown-файл.

Пример структуры:

```text
api-audit-report/
├── GET_api_users.md
├── POST_api_orders.md
├── DELETE_api_reports_reportId.md
├── PATCH_api_profile.md
└── SUMMARY.md
```

Каждый файл содержит:
- endpoint
- найденную реализацию
- проверки требований
- доказательства из кода
- статус выполнения

`SUMMARY.md` содержит:
- список всех API
- общий статус
- сколько требований выполнено
- сколько нарушений найдено
- ссылки на файлы отчётов

---

# ПРАВИЛО ИНИЦИАЛИЗАЦИИ

## Если `gigacode.md` отсутствует

НЕМЕДЛЕННО выполнить:

```bash
/init
```

После этого:
1. убедиться, что `gigacode.md` появился
2. прочитать `gigacode.md`
3. извлечь архитектурную информацию
4. только потом продолжать аудит API

---

# ПРАВИЛО АНАЛИЗА АРХИТЕКТУРЫ

Перед проверкой API ОБЯЗАТЕЛЬНО:

1. Прочитать `gigacode.md`
2. Определить:
   - слои приложения
   - архитектурный стиль
   - расположение controllers/resources/routes
   - сервисный слой
   - persistence layer
   - security layer
   - DTO/models/entities
   - API gateway/router
   - middleware/interceptors
   - validation layer

3. Использовать эти знания при поиске реализаций API.

Запрещено искать API вслепую.

---

# ВАЖНЫЕ ПРАВИЛА

- Каждое действие заканчивается блоком статуса
- Каждое требование должно иметь доказательство из кода
- Без доказательства нельзя ставить ✅
- Читать РЕАЛЬНЫЙ код файлов
- Не угадывать реализацию по именам
- Пути всегда относительные
- Не писать финальные API-отчёты в `gigacode.md`
- `gigacode.md` используется только как архитектурная база знаний

---

# СКРИПТЫ

В папке `scripts/` используются:

| Скрипт | Назначение |
|---|---|
| `scan_project.py` | анализ архитектуры проекта |
| `find_implementation.py` | поиск реализации API |
| `update_gigacode.py` | обновление архитектурных секций |

---

# ШАГ 0 — Проверка gigacode.md

Проверить:

```bash
ls gigacode.md
```

Если файла нет:

```bash
/init
```

После этого:

```bash
cat gigacode.md
```

Изучить:
- архитектуру
- сервисы
- слои
- routing
- dependency graph
- API structure
- modules
- security
- validation

Только потом переходить дальше.

---

# ШАГ 1 — Анализ проекта

Запустить:

```bash
python scripts/scan_project.py <project_root>
```

Получить:
- framework
- language
- build_tool
- api_files
- source_files
- dir_tree

Если нужно — обновить архитектурную секцию в `gigacode.md`.

НО:
- НЕ писать туда результаты аудита API
- НЕ писать endpoint-отчёты

---

# ШАГ 2 — Чтение файла типов API

Прочитать файл с типами API.

Для КАЖДОГО API:
1. выделить endpoint
2. выделить method
3. выделить требования
4. выделить ограничения
5. выделить security expectations
6. выделить validation expectations

---

# ШАГ 3 — Поиск реализации

Для каждого API:

```bash
python scripts/find_implementation.py <project_root> <METHOD> <path>
```

Использовать:
- знания из `gigacode.md`
- архитектуру проекта
- структуру слоёв

---

# ШАГ 4 — Создание ОТДЕЛЬНОГО отчёта

Создать папку:

```text
api-audit-report/
```

Для каждого API:

```text
api-audit-report/<METHOD>_<endpoint>.md
```

Пример:

```text
api-audit-report/POST_api_orders.md
```

Структура файла:

```md
# POST /api/orders

## Реализация
- File: src/main/java/.../OrderController.java
- Method: createOrder
- Lines: 44-81

## Проверка требований

### Требование: JWT authentication
✅ Выполнено
Доказательство:
```java
@PreAuthorize("hasRole('USER')")
```

### Требование: Validation
❌ Не выполнено
Доказательство:
validation annotations отсутствуют
```

---

# ШАГ 5 — SUMMARY.md

Создать:

```text
api-audit-report/SUMMARY.md
```

Содержимое:
- список API
- статус по каждому
- количество нарушений
- количество выполненных требований
- ссылки на markdown-файлы

---

# ЗАПРЕЩЕНО

❌ Записывать endpoint-аудит в `gigacode.md`
❌ Создавать один гигантский markdown-отчёт
❌ Искать API без анализа архитектуры
❌ Ставить ✅ без доказательства
❌ Игнорировать `/init`, если `gigacode.md` отсутствует

---

# РЕЗУЛЬТАТ

После завершения:

1. `gigacode.md`
   - содержит только архитектуру
   - используется как knowledge base

2. `api-audit-report/`
   - содержит полный аудит
   - отдельный `.md` на каждый API
   - содержит `SUMMARY.md`
```

---

# Обновлённый `update_gigacode.py`

```python
"""
update_gigacode.py — Используется ТОЛЬКО для архитектурного анализа.

ВАЖНО:
- НЕ хранит endpoint audit reports
- НЕ хранит результаты проверок API
- НЕ хранит compliance audit
- Используется только как архитектурная knowledge base
"""

import sys
import json
import argparse
import re
from pathlib import Path

GIGACODE_HEADER = "# GigaCode — Архитектурный анализ проекта\n\n"
SECTION_LEVEL = "##"

FORBIDDEN_SECTION_PATTERNS = [
    r"GET\s+/",
    r"POST\s+/",
    r"PUT\s+/",
    r"DELETE\s+/",
    r"PATCH\s+/",
    r"endpoint",
    r"audit",
    r"requirement",
    r"compliance",
]


def validate_section_title(title: str):
    lower = title.lower()

    for pattern in FORBIDDEN_SECTION_PATTERNS:
        if re.search(pattern, lower):
            raise ValueError(
                "gigacode.md предназначен только для архитектурного анализа. "
                "Endpoint audit reports запрещено сохранять в gigacode.md"
            )


def make_section(title: str, content: str) -> str:
    content = content.strip()
    return f"{SECTION_LEVEL} {title}\n\n{content}\n"


def section_pattern(title: str) -> re.Pattern:
    escaped = re.escape(title)

    return re.compile(
        rf"^{re.escape(SECTION_LEVEL)}\s+{escaped}\s*\n.*?(?=^{re.escape(SECTION_LEVEL)}\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )


def read_gigacode(path: Path) -> str:
    if not path.exists():
        return ""

    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def write_gigacode(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def update(gigacode_path: str, section_title: str, content: str) -> dict:
    validate_section_title(section_title)

    path = Path(gigacode_path)
    existing = read_gigacode(path)

    new_section = make_section(section_title, content)
    pat = section_pattern(section_title)

    if not existing:
        result_content = GIGACODE_HEADER + new_section
        write_gigacode(path, result_content)

        return {
            "status": "created",
            "file": str(path),
            "section": section_title,
            "message": "gigacode.md создан как архитектурная knowledge base"
        }

    if pat.search(existing):
        updated = pat.sub(new_section, existing)

        if not updated.endswith("\n"):
            updated += "\n"

        write_gigacode(path, updated)

        return {
            "status": "updated",
            "file": str(path),
            "section": section_title,
            "message": "Архитектурная секция обновлена"
        }

    separator = "\n" if existing.endswith("\n") else "\n\n"
    updated = existing + separator + new_section

    write_gigacode(path, updated)

    return {
        "status": "appended",
        "file": str(path),
        "section": section_title,
        "message": "Архитектурная секция добавлена"
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("gigacode_path")
    parser.add_argument("section_title")
    parser.add_argument("--content")
    parser.add_argument("--file")

    args = parser.parse_args()

    content = ""

    if args.content:
        content = args.content
    elif args.file:
        content = Path(args.file).read_text(encoding="utf-8")
    else:
        content = sys.stdin.read()

    result = update(args.gigacode_path, args.section_title, content)

    print(json.dumps(result, ensure_ascii=False, indent=2))
```

