import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from app.core.config import settings


def setup_logger(name: str = "web_rag") -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    log_level = logging.DEBUG if settings.DEBUG else getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 创建日志目录
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（按天轮转）
    file_handler = RotatingFileHandler(
        log_dir / f"{name}.log",
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 错误日志单独记录
    error_handler = RotatingFileHandler(
        log_dir / f"{name}_error.log",
        maxBytes=50 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger


# 默认 logger
logger = setup_logger()


def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器"""
    if name:
        return setup_logger(f"web_rag.{name}")
    return logger


# 便捷函数
def log_debug(message: str, logger_name: str = None):
    get_logger(logger_name).debug(message)


def log_info(message: str, logger_name: str = None):
    get_logger(logger_name).info(message)


def log_warning(message: str, logger_name: str = None):
    get_logger(logger_name).warning(message)


def log_error(message: str, logger_name: str = None, exc_info: bool = True):
    get_logger(logger_name).error(message, exc_info=exc_info)


def log_critical(message: str, logger_name: str = None, exc_info: bool = True):
    get_logger(logger_name).critical(message, exc_info=exc_info)
