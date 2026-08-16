"""pytest 共享 fixture 定义。"""

import pytest
import sqlite3
from pathlib import Path

from src.database import connection
from src.database.schema import create_tables

# 测试目录路径
TESTS_DIR = Path(__file__).parent
@pytest.fixture
def default_thumbnail_path() -> Path:
    """返回默认缩略图路径（default.png）。"""
    return (TESTS_DIR / "default.png")

@pytest.fixture
def tmp_filepath() -> str:
    """返回测试图片路径（test_pic1.png）。"""
    return str(TESTS_DIR / "test_pic1.png")


@pytest.fixture
def tmp_filepath_2() -> str:
    """返回另一张测试图片路径（test_pic2.png）。"""
    return str(TESTS_DIR / "test_pic2.png")


@pytest.fixture
def tmp_filepath_copy() -> str:
    """返回 test_pic1.png 的副本（内容相同，用于测试哈希一致性）。"""
    return str(TESTS_DIR / "test_pic1_copy.png")


@pytest.fixture
def db(tmp_path):
    """使用临时数据库，隔离测试数据，避免污染真实的 data.db。

    每个测试用例都会获得一个全新的、空的数据库连接（含默认分类）。
    测试结束后恢复全局单例连接。
    """
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    create_tables(conn)

    # 临时替换全局单例连接
    original_conn = connection._db._conn
    original_path = connection._db.db_path
    connection._db._conn = conn
    connection._db.db_path = db_path

    yield conn

    # 恢复原连接
    connection._db._conn = original_conn
    connection._db.db_path = original_path
    conn.close()