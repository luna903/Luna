import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

CONFIG_FILE = Path.home() / ".zhao_config.json"

logger = logging.getLogger("config_store")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

def load_config() -> Dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info("配置加载成功: %s", str(CONFIG_FILE))
                return data
        except Exception:
            logger.exception("配置加载失败: %s", str(CONFIG_FILE))
    return {"source_folder": "", "sorted_folder": "", "history": [], "ignore_list": []}

def save_config(config: Dict[str, Any]) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info("配置保存成功: %s", str(CONFIG_FILE))
    except Exception:
        logger.exception("配置保存失败: %s", str(CONFIG_FILE))

def get_ignore_list_path(source_folder: str) -> Optional[Path]:
    if not source_folder:
        return None
    parent = Path(source_folder).parent
    ignore_folder = parent / "Игнор-лист"
    ignore_folder.mkdir(exist_ok=True)
    path = ignore_folder / "ignore_list.txt"
    logger.info("忽略列表路径: %s", str(path))
    return path

def load_ignore_list(source_folder: str) -> List[str]:
    p = get_ignore_list_path(source_folder)
    if p and p.exists():
        try:
            with open(p, "r", encoding="utf-8") as f:
                items = [line.strip() for line in f if line.strip()]
                logger.info("忽略列表加载: %d 条", len(items))
                return items
        except Exception:
            logger.exception("忽略列表加载失败: %s", str(p))
    return []

def save_ignore_list(source_folder: str, ignore_list: List[str]) -> None:
    p = get_ignore_list_path(source_folder)
    if p:
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write("\n".join(ignore_list))
            logger.info("忽略列表保存: %d 条 -> %s", len(ignore_list), str(p))
        except Exception:
            logger.exception("忽略列表保存失败: %s", str(p))