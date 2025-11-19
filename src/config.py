import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".zhao_config.json"


def load_config():
    """Загрузка конфигурации из файла"""

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")

    return {"source_folder": "", "sorted_folder": "", "history": [], "ignore_list": []}


def save_config(config):
    """Сохранение конфигурации в файл"""

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")


def get_ignore_list_path(source_folder):
    """Получение пути к файлу игнор-листа"""

    if not source_folder:
        return None
    parent = Path(source_folder).parent
    ignore_folder = parent / "Игнор-лист"
    ignore_folder.mkdir(exist_ok=True)

    return ignore_folder / "ignore_list.txt"


def load_ignore_list(source_folder):
    """Загрузка игнор-листа"""

    ignore_path = get_ignore_list_path(source_folder)
    if ignore_path and ignore_path.exists():
        try:
            with open(ignore_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Ошибка загрузки игнор-листа: {e}")

    return []


def save_ignore_list(source_folder, ignore_list):
    """Сохранение игнор-листа"""

    ignore_path = get_ignore_list_path(source_folder)
    if ignore_path:
        try:
            with open(ignore_path, "w", encoding="utf-8") as f:
                f.write("\n".join(ignore_list))
        except Exception as e:
            print(f"Ошибка сохранения игнор-листа: {e}")
