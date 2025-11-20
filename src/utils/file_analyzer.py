import os
from datetime import datetime
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - функция:%(funcName)s - содержание:%(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("analizator_faylov.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

def get_all_files(folder_path):

    files = []
    try:
        # 开始/начало
        logger.info("Начало рекурсивного сканирования папки：%s", folder_path)
        for root, _, filenames in os.walk(folder_path):
            # 调试级扫描进度/прогресс сканирования уровня отладки
            logger.debug("Сканирование подпапки：%s,найдено %d файлов", root, len(filenames))
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
                    logger.debug("Файл успешно добавлен：%s（размер：%s）", file_path, format_file_size(stat.st_size))
                except Exception as e:
                    logger.error("Ошибка обработки файла %s: %s", file_path, e)
    except Exception as e:
        logger.error("Ошибка сканирования папки %s: %s", folder_path, e)
    
    logger.info("Сканирование папки завершено：%s,собрано %d действительных файлов", folder_path, len(files))
    return files


def find_unsorted_files(source_files, sorted_files, ignore_list):
    """Определение неотсортированных файлов"""

    logger.info("Начало фильтрации неотсортированных файлов：общее количество исходных файлов=%d,общее количество отсортированных файлов=%d,список игнорируемых файлов=%s",
                len(source_files), len(sorted_files), ignore_list)
    sorted_names = {os.path.basename(f["path"]) for f in sorted_files}

    unsorted = []
    for file_info in source_files:
        filename = file_info["name"]
        if filename not in ignore_list and filename not in sorted_names:
            unsorted.append(file_info)
            logger.debug("Найден неотсортированный файл：%s(путь：%s)", filename, file_info["path"])

    logger.info("Фильтрация неотсортированных файлов завершена,найдено %d неотсортированных файлов", len(unsorted))
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

    logger.info("Начало анализа неотсортированных файлов：исходная папка=%s,отсортированная папка=%s,список игнорируемых файлов=%s",
                source_folder, sorted_folder, ignore_list)
    if not os.path.exists(source_folder) or not os.path.exists(sorted_folder):
        logger.error("Папка не существует：существует ли исходная папка[%s]?%s；существует ли отсортированная папка[%s]？%s",
                    source_folder, os.path.exists(source_folder),
                    sorted_folder, os.path.exists(sorted_folder))
        raise FileNotFoundError("Одна из указанных папок не существует.")

    sorted_files = set(os.listdir(sorted_folder))
    logger.debug("Отсортированная папка содержит %d файлов", len(sorted_files))

    file_count = 0  # 统计总扫描文件数/Посчитать общее количество отсканированных файлов
    for root, _, files in os.walk(source_folder):
        file_count += len(files)
        for file in files:
            if file not in sorted_files and file not in ignore_list:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    file_mtime = os.path.getmtime(file_path)
                    unsorted_files.append(
                        {
                            "name": file,
                            "path": file_path,
                            "size": file_size,
                            "mtime": file_mtime,
                        }
                    )
                    logger.debug("Добавлен неотсортированный файл：%s(размер：%s,дата изменения：%s)",
                                file_path, format_file_size(file_size),
                                datetime.fromtimestamp(file_mtime).strftime("%Y-%m-%d %H:%M:%S"))
                except Exception as e:
                    logger.error("Ошибка чтения информации о файле：%s,причина ошибки：%s", file_path, str(e))

    logger.info("Анализ файлов завершен：всего отсканировано %d файлов в исходной папке,найдено %d неотсортированных файлов",
                file_count, len(unsorted_files))
    return unsorted_files