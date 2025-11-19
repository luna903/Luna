import os
from datetime import datetime


def get_all_files(folder_path):
    """Получение списка всех файлов рекурсивно"""

    files = []
    try:
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                try:
                    stat = os.stat(file_path)
                    files.append(
                        {
                            "path": file_path,
                            "name": filename,
                            "relative_path": os.path.relpath(file_path, folder_path),
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime),
                            "extension": os.path.splitext(filename)[1],
                        }
                    )
                except Exception as e:
                    print(f"Ошибка обработки файла {file_path}: {e}")
    except Exception as e:
        print(f"Ошибка сканирования папки {folder_path}: {e}")

    return files


def find_unsorted_files(source_files, sorted_files, ignore_list):
    """Определение неотсортированных файлов"""

    sorted_names = {os.path.basename(f["path"]) for f in sorted_files}

    unsorted = []
    for file_info in source_files:
        filename = file_info["name"]
        if filename not in ignore_list and filename not in sorted_names:
            unsorted.append(file_info)

    return unsorted


def format_file_size(size_bytes):
    """Форматирование размера файла"""

    for unit in ["Б", "КБ", "МБ", "ГБ", "ТБ"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.2f} ПБ"


def analyze_files(source_folder, sorted_folder, ignore_list):
    unsorted_files = []

    if not os.path.exists(source_folder) or not os.path.exists(sorted_folder):
        raise FileNotFoundError("Одна из указанных папок не существует.")

    sorted_files = set(os.listdir(sorted_folder))

    for root, _, files in os.walk(source_folder):
        for file in files:
            if file not in sorted_files and file not in ignore_list:
                file_path = os.path.join(root, file)
                unsorted_files.append(
                    {
                        "name": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "mtime": os.path.getmtime(file_path),
                    }
                )

    return unsorted_files
