"""
find_implementation.py — Шаг 3 аудита.

По типу API (метод + путь) ищет реализацию в коде тремя стратегиями.
Для каждого кандидата извлекает: файл, класс, метод, строки, сниппет.

Использование:
    python scripts/find_implementation.py <project_root> <method> <path> [--keywords word1,word2]

Примеры:
    python scripts/find_implementation.py /myproject POST /api/orders
    python scripts/find_implementation.py /myproject GET /api/users/{id} --keywords user,getUser
    python scripts/find_implementation.py /myproject DELETE /api/reports/{reportId}

Вывод: JSON в stdout
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path

# ─── Конфигурация ────────────────────────────────────────────────────────────

SOURCE_EXTENSIONS = {".java", ".kt", ".py", ".ts", ".js", ".go", ".cs", ".rb", ".php"}

SKIP_DIRS = {
    ".git", ".idea", ".vscode", "node_modules", "__pycache__",
    "target", "build", "dist", "out", ".gradle", ".mvn",
    "vendor", "venv", ".venv", "env",
}

# Аннотации HTTP-методов по фреймворкам
METHOD_PATTERNS = {
    "GET":    [r"@GetMapping", r"@RequestMapping.*GET", r"@app\.get", r"router\.get", r"r\.GET", r"@Get\("],
    "POST":   [r"@PostMapping", r"@RequestMapping.*POST", r"@app\.post", r"router\.post", r"r\.POST", r"@Post\("],
    "PUT":    [r"@PutMapping", r"@RequestMapping.*PUT", r"@app\.put", r"router\.put", r"r\.PUT", r"@Put\("],
    "DELETE": [r"@DeleteMapping", r"@RequestMapping.*DELETE", r"@app\.delete", r"router\.delete", r"r\.DELETE", r"@Delete\("],
    "PATCH":  [r"@PatchMapping", r"@RequestMapping.*PATCH", r"@app\.patch", r"router\.patch", r"r\.PATCH", r"@Patch\("],
}

CONTEXT_LINES = 40  # строк вокруг найденного места для сниппета


# ─── Утилиты ─────────────────────────────────────────────────────────────────

def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def read_lines(path: Path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()
    except Exception:
        return []


def all_source_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            p = Path(dirpath) / fname
            if p.suffix.lower() in SOURCE_EXTENSIONS:
                yield p


def normalize_path(api_path: str) -> list[str]:
    """
    Из пути /api/users/{id} делает несколько вариантов для поиска:
      /api/users/{id}   — оригинал
      /api/users/       — без параметра
      api/users         — без слешей
      users             — последний сегмент
    """
    variants = [api_path]
    # Убираем path-параметры: {id}, :id, <id>
    no_params = re.sub(r"\{[^}]+\}|:[a-zA-Z_]+|<[^>]+>", "", api_path)
    no_params = re.sub(r"//+", "/", no_params).rstrip("/")
    if no_params and no_params != api_path:
        variants.append(no_params)
    # Последний сегмент пути
    parts = [p for p in api_path.strip("/").split("/") if p and not p.startswith("{")]
    if parts:
        variants.append(parts[-1])
        if len(parts) >= 2:
            variants.append("/".join(parts[-2:]))
    return list(dict.fromkeys(variants))  # убираем дубли, сохраняем порядок


def extract_class_and_method(lines: list[str], hit_line: int) -> tuple[str, str]:
    """Ищет имя класса и метода вокруг найденной строки."""
    class_name = ""
    method_name = ""

    # Ищем метод — смотрим вниз от hit_line
    for i in range(hit_line, min(hit_line + 5, len(lines))):
        line = lines[i]
        # Java/Kotlin: public ResponseEntity<...> methodName(
        m = re.search(r"(?:public|private|protected|override)?\s+\S+\s+(\w+)\s*\(", line)
        if m:
            method_name = m.group(1)
            break
        # Python: def method_name(
        m = re.search(r"def\s+(\w+)\s*\(", line)
        if m:
            method_name = m.group(1)
            break
        # Go: func (r *Router) MethodName(
        m = re.search(r"func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(", line)
        if m:
            method_name = m.group(1)
            break

    # Ищем класс — идём вверх от hit_line
    for i in range(hit_line, max(0, hit_line - 50), -1):
        line = lines[i]
        # Java/Kotlin
        m = re.search(r"(?:class|interface|object)\s+(\w+)", line)
        if m:
            class_name = m.group(1)
            break

    return class_name, method_name


def make_candidate(path: Path, root: Path, line_idx: int, lines: list[str], strategy: str) -> dict:
    """Формирует объект-кандидат для результата."""
    start = max(0, line_idx - 2)
    end = min(len(lines), line_idx + CONTEXT_LINES)
    snippet = "".join(lines[start:end])

    class_name, method_name = extract_class_and_method(lines, line_idx)

    return {
        "file": rel(path, root),
        "line": line_idx + 1,
        "line_start": start + 1,
        "line_end": end,
        "class": class_name,
        "method": method_name,
        "strategy": strategy,
        "snippet": snippet,
    }


# ─── Стратегии поиска ────────────────────────────────────────────────────────

def strategy_a_by_path(files, root: Path, path_variants: list[str]) -> list[dict]:
    """Стратегия A: ищем путь как строку в коде."""
    results = []
    for fpath in files:
        lines = read_lines(fpath)
        for i, line in enumerate(lines):
            for variant in path_variants:
                if variant in line:
                    results.append(make_candidate(fpath, root, i, lines, "A: path string"))
                    break  # не дублируем по вариантам
    return results


def strategy_b_by_method_annotation(files, root: Path, http_method: str, path_variants: list[str]) -> list[dict]:
    """Стратегия B: ищем аннотацию HTTP-метода рядом с ключевым словом из пути."""
    patterns = METHOD_PATTERNS.get(http_method.upper(), [])
    if not patterns:
        return []

    method_re = re.compile("|".join(patterns), re.IGNORECASE)
    results = []

    for fpath in files:
        lines = read_lines(fpath)
        content = "".join(lines)

        # Файл должен содержать аннотацию метода
        if not method_re.search(content):
            continue

        # И хотя бы один вариант пути (последний сегмент)
        keyword = path_variants[-1] if path_variants else ""
        if keyword and keyword.lower() not in content.lower():
            continue

        # Находим конкретную строку с аннотацией
        for i, line in enumerate(lines):
            if method_re.search(line):
                results.append(make_candidate(fpath, root, i, lines, "B: method annotation + keyword"))

    return results


def strategy_c_by_class_name(files, root: Path, api_path: str) -> list[dict]:
    """Стратегия C: ищем класс/файл с именем, производным от пути."""
    # Из /api/orders → Order, Orders, OrderController, OrderResource
    parts = [p for p in api_path.strip("/").split("/") if p and not p.startswith("{") and p != "api" and p != "v1" and p != "v2"]
    if not parts:
        return []

    last = parts[-1].rstrip("s")  # убираем множественное число: orders → order
    candidates_names = [
        last, last + "s",
        last.capitalize(), last.capitalize() + "s",
        last.capitalize() + "Controller",
        last.capitalize() + "Resource",
        last.capitalize() + "Handler",
        last.capitalize() + "Router",
    ]

    results = []
    for fpath in files:
        stem = fpath.stem.lower()
        if any(name.lower() in stem for name in candidates_names):
            lines = read_lines(fpath)
            if lines:
                results.append(make_candidate(fpath, root, 0, lines, "C: class/file name"))

    return results


def strategy_d_by_path_param_variants(files, root: Path, api_path: str) -> list[dict]:
    """Стратегия D: для путей с параметрами ищем разные варианты записи."""
    # /users/{id} → ищем: users/{, users/", users/', @PathVariable, PathVariable("id")
    param_names = re.findall(r"\{(\w+)\}", api_path)
    if not param_names:
        return []

    segments = [p for p in api_path.strip("/").split("/") if not p.startswith("{")]
    if not segments:
        return []

    base = segments[-1]
    search_terms = [base] + [f'@PathVariable("{p}")' for p in param_names] + [f"@PathVariable {p}" for p in param_names]

    results = []
    for fpath in files:
        lines = read_lines(fpath)
        for i, line in enumerate(lines):
            if any(term.lower() in line.lower() for term in search_terms):
                results.append(make_candidate(fpath, root, i, lines, "D: path parameter variants"))
                break

    return results


# ─── Дедупликация ────────────────────────────────────────────────────────────

def deduplicate(candidates: list[dict]) -> list[dict]:
    """Убираем дубли по файлу (оставляем первый найденный для каждого файла)."""
    seen = set()
    unique = []
    for c in candidates:
        key = c["file"]
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


# ─── Основная логика ─────────────────────────────────────────────────────────

def find(project_root: str, http_method: str, api_path: str, extra_keywords: list[str] = None) -> dict:
    root = Path(project_root).resolve()
    if not root.exists():
        return {"error": f"Путь не существует: {project_root}"}

    path_variants = normalize_path(api_path)
    if extra_keywords:
        path_variants += extra_keywords

    files = list(all_source_files(root))
    strategies_used = []
    all_candidates = []

    # Стратегия A
    a = strategy_a_by_path(files, root, path_variants)
    strategies_used.append(f"A: поиск строки пути ({', '.join(path_variants[:3])})")
    all_candidates += a

    # Стратегия B
    b = strategy_b_by_method_annotation(files, root, http_method, path_variants)
    strategies_used.append(f"B: аннотация {http_method} + ключевое слово")
    all_candidates += b

    # Стратегия C
    c = strategy_c_by_class_name(files, root, api_path)
    strategies_used.append("C: имя класса/файла по сегменту пути")
    all_candidates += c

    # Стратегия D (только если есть path-параметры)
    if "{" in api_path:
        d = strategy_d_by_path_param_variants(files, root, api_path)
        strategies_used.append("D: варианты записи path-параметров")
        all_candidates += d

    candidates = deduplicate(all_candidates)

    return {
        "method": http_method.upper(),
        "path": api_path,
        "path_variants_searched": path_variants,
        "found": len(candidates) > 0,
        "candidates_count": len(candidates),
        "candidates": candidates,
        "strategies_used": strategies_used,
    }


# ─── Точка входа ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ищет реализацию API в проекте")
    parser.add_argument("project_root", help="Путь к корню проекта")
    parser.add_argument("method", help="HTTP-метод: GET, POST, PUT, DELETE, PATCH")
    parser.add_argument("path", help="Путь API, например /api/orders или /api/users/{id}")
    parser.add_argument("--keywords", help="Дополнительные ключевые слова через запятую", default="")

    args = parser.parse_args()
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else []

    result = find(args.project_root, args.method, args.path, keywords)
    print(json.dumps(result, ensure_ascii=False, indent=2))
