"""
scan_project.py — Шаг 1 аудита.

Сканирует проект, находит файлы с реализацией API, определяет фреймворк и стек.

Использование:
    python scripts/scan_project.py <project_root>
    python scripts/scan_project.py /home/user/myproject

Вывод: JSON в stdout
"""

import os
import sys
import json
import re
from pathlib import Path

# ─── Конфигурация ────────────────────────────────────────────────────────────

SOURCE_EXTENSIONS = {".java", ".kt", ".py", ".ts", ".js", ".go", ".cs", ".rb", ".php"}

SKIP_DIRS = {
    ".git", ".idea", ".vscode", "node_modules", "__pycache__",
    "target", "build", "dist", "out", ".gradle", ".mvn",
    "vendor", "venv", ".venv", "env", "coverage", ".pytest_cache",
}

# Паттерны имён файлов/папок, указывающие на API-реализацию
API_NAME_PATTERNS = [
    r"controller", r"resource", r"handler", r"router", r"routes",
    r"endpoint", r"rest", r"api", r"web", r"view", r"servlet",
]

# Фреймворки: (паттерн в содержимом файла, название фреймворка)
FRAMEWORK_SIGNATURES = [
    # Java
    (r"@RestController|@RequestMapping|@GetMapping|@PostMapping", "Java / Spring Boot"),
    (r"@Path\s*\(|@GET\s*\n|@POST\s*\n|javax\.ws\.rs|jakarta\.ws\.rs", "Java / JAX-RS"),
    (r"HttpServlet|doGet|doPost", "Java / Servlet"),
    # Kotlin
    (r"@RestController.*kotlin|import org\.springframework.*kotlin", "Kotlin / Spring Boot"),
    # Python
    (r"from fastapi|import fastapi|APIRouter|@app\.(get|post|put|delete)", "Python / FastAPI"),
    (r"from flask|import flask|@app\.route|Blueprint", "Python / Flask"),
    (r"from django|import django|urlpatterns", "Python / Django"),
    # Node.js
    (r"require\(['\"]express['\"]|from ['\"]express['\"]", "Node.js / Express"),
    (r"@Controller\(\)|@Get\(|@Post\(|NestFactory", "Node.js / NestJS"),
    # Go
    (r"gin\.Default\(\)|gin\.New\(\)|r\.GET\(|r\.POST\(", "Go / Gin"),
    (r"http\.HandleFunc|http\.ListenAndServe", "Go / net/http"),
]

# Сборщики/конфиги
BUILD_TOOL_FILES = {
    "pom.xml": "Maven",
    "build.gradle": "Gradle",
    "build.gradle.kts": "Gradle (Kotlin DSL)",
    "package.json": "npm/yarn",
    "go.mod": "Go modules",
    "requirements.txt": "pip",
    "pyproject.toml": "Poetry/pip",
    "Cargo.toml": "Cargo (Rust)",
}


# ─── Утилиты ─────────────────────────────────────────────────────────────────

def is_api_file(path: Path) -> bool:
    name = path.stem.lower()
    return any(re.search(pat, name) for pat in API_NAME_PATTERNS)


def read_safe(path: Path, max_bytes: int = 8192) -> str:
    """Читает начало файла, игнорирует бинарные."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_bytes)
    except Exception:
        return ""


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


# ─── Основная логика ─────────────────────────────────────────────────────────

def scan(project_root: str) -> dict:
    root = Path(project_root).resolve()
    if not root.exists():
        return {"error": f"Путь не существует: {project_root}"}

    all_source_files = []   # все исходники
    api_files = []          # файлы с API-реализацией (по имени)
    config_files = {}       # build/config файлы
    framework_votes = {}    # фреймворк → кол-во совпадений
    dir_tree = []           # дерево директорий (значимые части)

    for dirpath, dirnames, filenames in os.walk(root):
        # Пропускаем служебные директории
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        dp = Path(dirpath)
        level = len(dp.relative_to(root).parts)

        # Дерево: не глубже 4 уровней, чтобы не захламлять
        if level <= 4:
            indent = "  " * level
            dir_tree.append(f"{indent}{dp.name}/")

        for fname in filenames:
            fpath = dp / fname
            ext = fpath.suffix.lower()

            # Build/config файлы
            if fname in BUILD_TOOL_FILES:
                config_files[fname] = BUILD_TOOL_FILES[fname]

            # Только исходники
            if ext not in SOURCE_EXTENSIONS:
                continue

            rel_path = rel(fpath, root)
            all_source_files.append(rel_path)

            # Кандидаты на API-файлы по имени
            if is_api_file(fpath):
                api_files.append(rel_path)

            # Детект фреймворка по содержимому
            if level <= 6:  # не лезем слишком глубоко
                content = read_safe(fpath)
                for pattern, framework in FRAMEWORK_SIGNATURES:
                    if re.search(pattern, content, re.IGNORECASE):
                        framework_votes[framework] = framework_votes.get(framework, 0) + 1

    # Определяем фреймворк — берём с наибольшим числом совпадений
    detected_framework = "не определён"
    if framework_votes:
        detected_framework = max(framework_votes, key=framework_votes.get)

    # Определяем язык из фреймворка
    lang_map = {
        "Java": "Java", "Kotlin": "Kotlin", "Python": "Python",
        "Node.js": "JavaScript/TypeScript", "Go": "Go",
    }
    language = next((v for k, v in lang_map.items() if k in detected_framework), "неизвестен")

    # Определяем build tool
    build_tool = next(iter(config_files.values()), "не найден")

    return {
        "project_root": str(root),
        "language": language,
        "framework": detected_framework,
        "build_tool": build_tool,
        "config_files": list(config_files.keys()),
        "total_source_files": len(all_source_files),
        "api_files": api_files,
        "api_files_count": len(api_files),
        "all_source_files": all_source_files,
        "dir_tree": dir_tree[:80],  # ограничиваем размер вывода
        "framework_votes": framework_votes,
    }


# ─── Точка входа ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Укажи путь к проекту: python scan_project.py <project_root>"}))
        sys.exit(1)

    result = scan(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
