import logging
import sys
from logging.handlers import RotatingFileHandler

from src.utils.path import get_logs_dir

_LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_DEFAULT_LEVEL = logging.INFO

_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
_BACKUP_COUNT = 5  # 保留最近的 5 个日志文件

_initialized = False

def setup_logging(level: int = _DEFAULT_LEVEL):
    """配置全局日志系统。

    同时输出到控制台和日志文件（logs/app.log）。
    使用 RotatingFileHandler 实现日志轮转，避免文件无限增长。

    :param level: 日志级别，默认 INFO
    """
    global _initialized
    if _initialized:
        return

    # 创建日志目录（如果不存在）
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 设置日志格式
    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器（带滚动功能）
    log_dir = get_logs_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "app.log"
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    _initialized = True

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器。

    :param name: 日志记录器名称
    :return: 日志记录器对象
    """
    setup_logging()
    return logging.getLogger(name)