"""数据库层：连接管理、建表、数据访问。"""

from database.connection import Database, get_db, get_connection
from database.schema import create_tables
from database.repository import (
    categories,
    tags,
    images,
    image_tags,
    search,
    CategoryRepository,
    TagRepository,
    ImageRepository,
    ImageTagRepository,
    SearchRepository,
    categories,
    tags,
    images,
    image_tags,
    search,
)

__all__ = [
    "Database",
    "get_db",
    "get_connection",
    "create_tables",
    "categories",
    "tags",
    "images",
    "image_tags",
    "search",
    "CategoryRepository",
    "TagRepository",
    "ImageRepository",
    "ImageTagRepository",
    "SearchRepository",
]