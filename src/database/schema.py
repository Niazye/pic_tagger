"""数据库建表 SQL 与初始化。"""

import sqlite3
from src.utils.logger import get_logger

logger = get_logger(__name__)

# 默认分类（"未分类"）的固定 id 与名称
DEFAULT_CATEGORY_ID = 1
DEFAULT_CATEGORY_NAME = "未分类"

# 建表语句（与设计文档 3.3 节一致）
SCHEMA_SQL = """
-- 标签分类表
CREATE TABLE IF NOT EXISTS categories (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL UNIQUE,
    color_hex     TEXT,
    sort_order    INTEGER DEFAULT 0,
    category_type TEXT    NOT NULL DEFAULT 'free'
);

-- 标签表
CREATE TABLE IF NOT EXISTS tags (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name        TEXT    NOT NULL,
    url         TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    UNIQUE (category_id, name)
);

-- 图片表
CREATE TABLE IF NOT EXISTS images (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path   TEXT    NOT NULL,
    file_hash   TEXT    NOT NULL,
    file_name   TEXT,
    description TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    file_size   INTEGER,
    width       INTEGER,
    height      INTEGER,
    file_mtime  DATETIME,
    is_missing  INTEGER NOT NULL DEFAULT 0
);

-- 图片-标签关联表
CREATE TABLE IF NOT EXISTS image_tags (
    image_id INTEGER NOT NULL,
    tag_id   INTEGER NOT NULL,
    PRIMARY KEY (image_id, tag_id),
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id)   REFERENCES tags(id)   ON DELETE CASCADE
);

-- 索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_name ON categories(name);
CREATE UNIQUE INDEX IF NOT EXISTS idx_tags_category_name ON tags(category_id, name);
CREATE INDEX IF NOT EXISTS idx_image_tags ON image_tags(image_id, tag_id);
CREATE INDEX IF NOT EXISTS idx_images_hash ON images(file_hash);
"""


def create_tables(conn: sqlite3.Connection) -> None:
    """在给定连接上执行建表语句。"""
    conn.executescript(SCHEMA_SQL)
    # 自动创建默认分类（"未分类"），幂等（INSERT OR IGNORE）
    conn.execute(
        "INSERT OR IGNORE INTO categories (id, name, sort_order, category_type) "
        "VALUES (?, ?, 0, 'free')",
        (DEFAULT_CATEGORY_ID, DEFAULT_CATEGORY_NAME),
    )
    conn.commit()
    logger.info("数据库表结构初始化完成")