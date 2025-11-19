import os
import shutil
from pathlib import Path
from datetime import datetime


def create_result_folder(base_path):
    """Создание папки результата с временной меткой"""

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"неотсортированное-{timestamp}"
    result_path = Path(base_path).parent / folder_name
    result_path.mkdir(parents=True, exist_ok=True)

    return str(result_path)


def copy_unsorted_files(unsorted_files, source_folder, dest_folder):
    """Копирование неотсортированных файлов с сохранением структуры"""

    copied = 0
    errors = []

    for file_info in unsorted_files:
        try:
            source_path = file_info["path"]
            relative_path = file_info["relative_path"]
            dest_path = Path(dest_folder) / relative_path

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            copied += 1
        except Exception as e:
            errors.append(f"Ошибка копирования {file_info['name']}: {e}")
            print(errors[-1])

    return copied, errors


def copy_file(src, dest):
    """Copy a file from src to dest."""

    shutil.copy2(src, dest)


def move_file(src, dest):
    """Move a file from src to dest."""

    shutil.move(src, dest)


def delete_file(file_path):
    """Delete a file at the specified path."""

    os.remove(file_path)


def get_file_size(file_path):
    """Return the size of the file at the specified path."""

    return os.path.getsize(file_path)


def get_file_modification_time(file_path):
    """Return the last modification time of the file at the specified path."""

    return os.path.getmtime(file_path)
