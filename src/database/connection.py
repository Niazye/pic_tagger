"""数据库连接管理。"""

import sqlite3
from pathlib import Path

from src.utils.path import get_db_path, ensure_dirs
from src.database import create_tables
from src.utils.logger import get_logger

logger = get_logger(__name__)


class Database:
    """SQLite 数据库连接管理器。

    提供单例连接，供各 Repository 复用。
    """

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_db_path()
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> sqlite3.Connection:
        """建立连接并初始化表结构。"""
        if self._conn is not None:
            return self._conn

        ensure_dirs()
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        # 启用外键约束（SQLite 默认关闭）
        self._conn.execute("PRAGMA foreign_keys = ON")
        # 返回字典形式的行，便于按列名访问
        self._conn.row_factory = sqlite3.Row
        create_tables(self._conn)
        logger.info(f"数据库连接已建立: {self.db_path}")
        return self._conn

    @property
    def conn(self) -> sqlite3.Connection:
        """获取连接（自动建立）。"""
        return self.connect()

    def close(self) -> None:
        """关闭连接。"""
        if self._conn is not None:
            self._conn.close()
            logger.info(f"数据库连接已关闭: {self.db_path}")
            self._conn = None

    def transaction(self):
        """返回一个事务上下文管理器。"""
        return self._conn


# 全局单例
_db = Database()


def get_db() -> Database:
    """获取全局数据库实例。"""
    return _db


def get_connection() -> sqlite3.Connection:
    """获取全局数据库连接。"""
    return _db.conn