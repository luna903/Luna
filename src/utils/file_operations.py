import os
import shutil
from pathlib import Path
from datetime import datetime
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - функция:%(funcName)s - содержание:%(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("operatsii_s_faylami.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

def create_result_folder(base_path):
    logger.info("Начало создания папки с результатами，базовый путь：%s", base_path)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"неотсортированное-{timestamp}"
    result_path = Path(base_path).parent / folder_name
    result_path.mkdir(parents=True, exist_ok=True)

    logger.info("Папка с результатами успешно создана，путь：%s", str(result_path))
    return str(result_path)


def copy_unsorted_files(unsorted_files, source_folder, dest_folder):
    """Копирование неотсортированных файлов с сохранением структуры按结构复制未排序的文件"""
    logger.info("Начало копирования неотсортированных файлов，количество файлов для копирования：%d，исходная папка：%s，целевая папка：%s",
                len(unsorted_files), source_folder, dest_folder)

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
            logger.debug("Файл успешно скопирован：исходный путь=%s → целевой путь=%s", source_path, str(dest_path))
        except Exception as e:
            error_msg = f"Ошибка копирования {file_info['name']}: {e}"
            errors.append(error_msg)
            logger.error(error_msg)

    # 记录复制结果/Запись результатов копирования
    logger.info("Копирование неотсортированных файлов завершено，скопировано файлов：%d，количество ошибок：%d", copied, len(errors))
    if errors:
        logger.warning("Детали ошибок копирования：%s", "; ".join(errors[:5]))  # 以免日志过载/Логируем первые 5 ошибок，чтобы не перегружать лог
    return copied, errors


def copy_file(src, dest):
    """Copy a file from src to dest."""
    # 记录开始/Запись началась
    logger.info("Начало копирования файла：исходный путь=%s → целевой путь=%s", src, dest)
    try:
        shutil.copy2(src, dest)
        logger.debug("Файл успешно скопирован：%s → %s", src, dest)
    except Exception as e:
        # 复制错误/ошибка копирования
        logger.error("Ошибка копирования файла %s → %s: %s", src, dest, str(e))
        raise  

def move_file(src, dest):
    # 记录开始单个文件移动/запись о начале перемещения отдельного файла
    logger.info("Начало перемещения файла：исходный путь=%s → целевой путь=%s", src, dest)
    try:
        shutil.move(src, dest)
        logger.debug("Файл успешно перемещен：%s → %s", src, dest)
    except Exception as e:
        logger.error("Ошибка перемещения файла %s → %s: %s", src, dest, str(e))
        raise  

def delete_file(file_path):
    # 开始删除文件/Начать удаление файлов
    logger.info("Начало удаления файла：путь=%s", file_path)
    try:
        os.remove(file_path)
        logger.debug("Файл успешно удален：%s", file_path)
    except Exception as e:
        logger.error("Ошибка удаления файла %s: %s", file_path, str(e))
        raise 

def get_file_size(file_path):
    logger.debug("Получение размера файла：путь=%s", file_path)
    try:
        size = os.path.getsize(file_path)
        logger.debug("Размер файла %s: %s байт", file_path, size)
        return size
    except Exception as e:
        logger.error("Ошибка получения размера файла %s: %s", file_path, str(e))
        raise 

def get_file_modification_time(file_path):
    """Return the last modification time of the file at the specified path."""
    # 记录开始时间/запись о начале перемещения отдельного файла
    logger.debug("Получение времени последней модификации файла：путь=%s", file_path)
    try:
        mtime = os.path.getmtime(file_path)
        formatted_mtime = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        logger.debug("Время последней модификации файла %s: %s", file_path, formatted_mtime)
        return mtime
    except Exception as e:
        logger.error("Ошибка получения времени последней модификации файла %s: %s", file_path, str(e))
        raise  