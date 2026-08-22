"""数据访问层（Repository）。

提供对 categories / tags / images / image_tags 四张表的增删改查。
所有方法均使用参数化 SQL，防止注入。
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from src.database import get_connection
from src.models import Category, Tag, Image


def _row_to_category(row: sqlite3.Row) -> Category:
    return Category(
        id=row["id"],
        name=row["name"],
        color_hex=row["color_hex"],
        sort_order=row["sort_order"],
        category_type=row["category_type"],
    )


def _row_to_tag(row: sqlite3.Row) -> Tag:
    return Tag(
        id=row["id"],
        category_id=row["category_id"],
        name=row["name"],
        url=row["url"],
    )


def _row_to_image(row: sqlite3.Row) -> Image:
    return Image(
        id=row["id"],
        file_path=row["file_path"],
        file_hash=row["file_hash"],
        file_name=row["file_name"],
        description=row["description"],
        created_at=_parse_datetime(row["created_at"]),
        file_size=row["file_size"],
        width=row["width"],
        height=row["height"],
        file_mtime=_parse_datetime(row["file_mtime"]),
        is_missing=row["is_missing"],
    )

def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


# ============================================================
# categories 表
# ============================================================

class CategoryRepository:
    def create(self, name: str, category_type: str = "free",
               color_hex: str | None = None, sort_order: int = 0) -> Category:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO categories (name, color_hex, sort_order, category_type) "
            "VALUES (?, ?, ?, ?)",
            (name, color_hex, sort_order, category_type),
        )
        conn.commit()
        return Category(id=cur.lastrowid, name=name, color_hex=color_hex,
                        sort_order=sort_order, category_type=category_type)

    def get_by_id(self, category_id: int) -> Category | None:
        row = get_connection().execute(
            "SELECT * FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        return _row_to_category(row) if row else None

    def get_by_name(self, name: str) -> Category | None:
        row = get_connection().execute(
            "SELECT * FROM categories WHERE name = ?", (name,)
        ).fetchone()
        return _row_to_category(row) if row else None

    def get_all(self) -> list[Category]:
        rows = get_connection().execute(
            "SELECT * FROM categories ORDER BY sort_order, id"
        ).fetchall()
        return [_row_to_category(r) for r in rows]

    def rename(self, category_id: int, new_name: str) -> None:
        conn = get_connection()
        conn.execute("UPDATE categories SET name = ? WHERE id = ?",
                     (new_name, category_id))
        conn.commit()

    def set_color(self, category_id: int, color_hex: str) -> None:
        conn = get_connection()
        conn.execute("UPDATE categories SET color_hex = ? WHERE id = ?",
                     (color_hex, category_id))
        conn.commit()

    def set_sort_order(self, category_id: int, sort_order: int) -> None:
        conn = get_connection()
        conn.execute("UPDATE categories SET sort_order = ? WHERE id = ?",
                     (sort_order, category_id))
        conn.commit()

    def delete(self, category_id: int) -> None:
        """删除分类（级联删除其下标签及关联）。"""
        conn = get_connection()
        conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()


# ============================================================
# tags 表
# ============================================================

class TagRepository:
    def create(self, category_id: int, name: str, url: str | None = None) -> Tag:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO tags (category_id, name, url) VALUES (?, ?, ?)",
            (category_id, name, url),
        )
        conn.commit()
        return Tag(id=cur.lastrowid, category_id=category_id, name=name, url=url)

    def get_by_id(self, tag_id: int) -> Tag | None:
        row = get_connection().execute(
            "SELECT * FROM tags WHERE id = ?", (tag_id,)
        ).fetchone()
        return _row_to_tag(row) if row else None

    def get_by_category_and_name(self, category_id: int, name: str) -> Tag | None:
        row = get_connection().execute(
            "SELECT * FROM tags WHERE category_id = ? AND name = ?",
            (category_id, name),
        ).fetchone()
        return _row_to_tag(row) if row else None

    def get_by_category(self, category_id: int) -> list[Tag]:
        rows = get_connection().execute(
            "SELECT * FROM tags WHERE category_id = ? ORDER BY name",
            (category_id,),
        ).fetchall()
        return [_row_to_tag(r) for r in rows]

    def get_all(self) -> list[Tag]:
        rows = get_connection().execute(
            "SELECT * FROM tags ORDER BY category_id, name"
        ).fetchall()
        return [_row_to_tag(r) for r in rows]

    def rename(self, tag_id: int, new_name: str) -> None:
        conn = get_connection()
        conn.execute("UPDATE tags SET name = ? WHERE id = ?", (new_name, tag_id))
        conn.commit()

    def set_url(self, tag_id: int, url: str) -> None:
        conn = get_connection()
        conn.execute("UPDATE tags SET url = ? WHERE id = ?", (url, tag_id))
        conn.commit()

    def delete(self, tag_id: int) -> None:
        """删除标签（级联删除关联）。"""
        conn = get_connection()
        conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        conn.commit()

    def move_to_category(self, tag_id: int, new_category_id: int) -> None:
        """将标签迁移到其他分类。"""
        conn = get_connection()
        conn.execute("UPDATE tags SET category_id = ? WHERE id = ?",
                     (new_category_id, tag_id))
        conn.commit()

    def autocomplete(self, category_id: int, prefix: str, limit: int = 20) -> list[str]:
        """按前缀自动补全该分类下的标签名。"""
        rows = get_connection().execute(
            "SELECT name FROM tags WHERE category_id = ? AND name LIKE ? "
            "ORDER BY name LIMIT ?",
            (category_id, f"{prefix}%", limit),
        ).fetchall()
        return [r["name"] for r in rows]


# ============================================================
# images 表
# ============================================================

class ImageRepository:
    def create(self, image: Image) -> Image:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO images (file_path, file_hash, file_name, description, "
            "file_size, width, height, file_mtime, is_missing) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (image.file_path, image.file_hash, image.file_name, image.description,
             image.file_size, image.width, image.height, image.file_mtime,
             image.is_missing),
        )
        conn.commit()
        image.id = cur.lastrowid # type: ignore
        return image

    def get_by_name(self, image_name: str) -> list[Image]:
        row = get_connection().execute(
            "SELECT * FROM images WHERE name = ?", (image_name, )
        ).fetchall()
        return [_row_to_image(r) for r in row]
    def get_by_name_keyword(self, keyword: str) -> list[Image]:
        row = get_connection().execute(
            "SELECT * FROM images WHERE name LIKE '%?%'", (keyword,)
        ).fetchall()
        return [_row_to_image(r) for r in row]
    def get_by_id(self, image_id: int) -> Image | None:
        row = get_connection().execute(
            "SELECT * FROM images WHERE id = ?", (image_id,)
        ).fetchone()
        return _row_to_image(row) if row else None

    def get_by_hash(self, file_hash: str) -> Image | None:
        row = get_connection().execute(
            "SELECT * FROM images WHERE file_hash = ?", (file_hash,)
        ).fetchone()
        return _row_to_image(row) if row else None

    def get_by_path(self, file_path: str) -> Image | None:
        row = get_connection().execute(
            "SELECT * FROM images WHERE file_path = ?", (file_path,)
        ).fetchone()
        return _row_to_image(row) if row else None

    def get_all(self) -> list[Image]:
        rows = get_connection().execute(
            "SELECT * FROM images ORDER BY created_at DESC, id DESC"
        ).fetchall()
        return [_row_to_image(r) for r in rows]

    def get_missing(self) -> list[Image]:
        rows = get_connection().execute(
            "SELECT * FROM images WHERE is_missing = 1"
        ).fetchall()
        return [_row_to_image(r) for r in rows]

    def update(self, image: Image) -> None:
        conn = get_connection()
        conn.execute(
            "UPDATE images SET file_path = ?, file_hash = ?, file_name = ?, "
            "description = ?, file_size = ?, width = ?, height = ?, "
            "file_mtime = ?, is_missing = ? WHERE id = ?",
            (image.file_path, image.file_hash, image.file_name, image.description,
             image.file_size, image.width, image.height, image.file_mtime,
             image.is_missing, image.id),
        )
        conn.commit()

    def update_description(self, image_id: int, description: str) -> None:
        conn = get_connection()
        conn.execute("UPDATE images SET description = ? WHERE id = ?",
                     (description, image_id))
        conn.commit()

    def set_missing(self, image_id: int, is_missing: bool) -> None:
        conn = get_connection()
        conn.execute("UPDATE images SET is_missing = ? WHERE id = ?",
                     (1 if is_missing else 0, image_id))
        conn.commit()

    def delete(self, image_id: int) -> None:
        """删除图片索引（级联删除关联）。"""
        conn = get_connection()
        conn.execute("DELETE FROM images WHERE id = ?", (image_id,))
        conn.commit()

    def delete_many(self, image_ids: list[int]) -> None:
        """批量删除图片索引。"""
        if not image_ids:
            return
        conn = get_connection()
        placeholders = ",".join("?" * len(image_ids))
        conn.execute(f"DELETE FROM images WHERE id IN ({placeholders})", image_ids)
        conn.commit()


# ============================================================
# image_tags 表
# ============================================================

class ImageTagRepository:
    def add(self, image_id: int, tag_id: int) -> None:
        """为图片添加标签（重复添加自动忽略）。"""
        conn = get_connection()
        conn.execute(
            "INSERT OR IGNORE INTO image_tags (image_id, tag_id) VALUES (?, ?)",
            (image_id, tag_id),
        )
        conn.commit()

    def add_many(self, image_ids: list[int], tag_id: int) -> None:
        """批量为一组图片添加同一标签。"""
        if not image_ids:
            return
        conn = get_connection()
        conn.executemany(
            "INSERT OR IGNORE INTO image_tags (image_id, tag_id) VALUES (?, ?)",
            [(iid, tag_id) for iid in image_ids],
        )
        conn.commit()

    def remove(self, image_id: int, tag_id: int) -> None:
        conn = get_connection()
        conn.execute(
            "DELETE FROM image_tags WHERE image_id = ? AND tag_id = ?",
            (image_id, tag_id),
        )
        conn.commit()

    def remove_many(self, image_ids: list[int], tag_id: int) -> None:
        """批量从一组图片移除同一标签。"""
        if not image_ids:
            return
        conn = get_connection()
        placeholders = ",".join("?" * len(image_ids))
        conn.execute(
            f"DELETE FROM image_tags WHERE tag_id = ? AND image_id IN ({placeholders})",
            [tag_id, *image_ids],
        )
        conn.commit()

    def get_tags_from_image(self, image_id: int) -> list[Tag]:
        rows = get_connection().execute(
            "SELECT t.* FROM tags t "
            "JOIN image_tags it ON it.tag_id = t.id "
            "WHERE it.image_id = ? ORDER BY t.name",
            (image_id,),
        ).fetchall()
        return [_row_to_tag(r) for r in rows]

    def get_images_from_tag(self, tag_id: int) -> list[Image]:
        rows = get_connection().execute(
            "SELECT i.* FROM images i "
            "JOIN image_tags it ON it.image_id = i.id "
            "WHERE it.tag_id = ? ORDER BY i.created_at DESC",
            (tag_id,),
        ).fetchall()
        return [_row_to_image(r) for r in rows]

    def get_image_tags_grouped_by_category(self, image_id: int) -> dict[int, list[Tag]]:
        """按分类分组返回图片的标签。"""
        rows = get_connection().execute(
            "SELECT t.*, c.id AS cid FROM tags t "
            "JOIN image_tags it ON it.tag_id = t.id "
            "JOIN categories c ON c.id = t.category_id "
            "WHERE it.image_id = ? ORDER BY c.sort_order, t.name",
            (image_id,),
        ).fetchall()
        grouped: dict[int, list[Tag]] = {}
        for r in rows:
            grouped.setdefault(r["cid"], []).append(_row_to_tag(r))
        return grouped

    def count_images_from_tag(self, tag_id: int) -> int:
        row = get_connection().execute(
            "SELECT COUNT(*) AS cnt FROM image_tags WHERE tag_id = ?", (tag_id,)
        ).fetchone()
        return row["cnt"] if row else 0


# ============================================================
# 搜索（组合查询）
# ============================================================

class SearchRepository:
    def search_by_keyword(self, keyword: str) -> list[Image]:
        """在文件名或标签名中模糊搜索。"""
        like = f"%{keyword}%"
        rows = get_connection().execute(
            "SELECT DISTINCT i.* FROM images i "
            "LEFT JOIN image_tags it ON it.image_id = i.id "
            "LEFT JOIN tags t ON t.id = it.tag_id "
            "WHERE i.file_name LIKE ? OR t.name LIKE ? "
            "ORDER BY i.created_at DESC",
            (like, like),
        ).fetchall()
        return [_row_to_image(r) for r in rows]

    def search_by_tags(self, conditions: list[tuple[int, str]], logic: str = "AND") -> list[Image]:
        """按标签条件搜索。

        conditions: [(category_id, tag_name), ...]
        logic: 'AND'（交集）或 'OR'（并集）
        """
        conn = get_connection()
        if not conditions:
            # 没有条件，返回全部结果
            rows = conn.execute(
                "SELECT * FROM images ORDER BY created_at DESC"
            ).fetchall()
            return [_row_to_image(r) for r in rows]

        if logic.upper() == "OR":
            # 并集：满足任一条件
            where_parts = []
            params: list = []
            for cid, name in conditions:
                where_parts.append("(t.category_id = ? AND t.name = ?)")
                params.extend([cid, name])
            sql = (
                "SELECT DISTINCT i.* FROM images i "
                "JOIN image_tags it ON it.image_id = i.id "
                "JOIN tags t ON t.id = it.tag_id "
                f"WHERE {' OR '.join(where_parts)} "
                "ORDER BY i.created_at DESC"
            )
        else:
            # 交集：同时满足所有条件
            sql = "SELECT i.* FROM images i WHERE "
            where_parts = []
            params = []
            for cid, name in conditions:
                where_parts.append(
                    "EXISTS (SELECT 1 FROM image_tags it JOIN tags t ON t.id = it.tag_id "
                    "WHERE it.image_id = i.id AND t.category_id = ? AND t.name = ?)"
                )
                params.extend([cid, name])
            sql += " AND ".join(where_parts) + " ORDER BY i.created_at DESC"

        rows = conn.execute(sql, params).fetchall()
        return [_row_to_image(r) for r in rows]

    def combined_search(self, keyword: str | None,
                        conditions: list[tuple[int, str]] | None,
                        logic: str = "AND") -> list[Image]:
        """组合搜索：关键词 + 标签条件。"""
        if not keyword and not conditions:
            return []

        conn = get_connection()
        where_parts = []
        params: list = []

        if keyword:
            like = f"%{keyword}%"
            where_parts.append(
                "(i.file_name LIKE ? OR EXISTS (SELECT 1 FROM image_tags it "
                "JOIN tags t ON t.id = it.tag_id WHERE it.image_id = i.id "
                "AND t.name LIKE ?))"
            )
            params.extend([like, like])

        if conditions:
            if logic.upper() == "OR":
                or_parts = []
                for cid, name in conditions:
                    or_parts.append("(t.category_id = ? AND t.name = ?)")
                    params.extend([cid, name])
                where_parts.append(
                    "EXISTS (SELECT 1 FROM image_tags it JOIN tags t ON t.id = it.tag_id "
                    f"WHERE it.image_id = i.id AND ({' OR '.join(or_parts)}))"
                )
            else:
                for cid, name in conditions:
                    where_parts.append(
                        "EXISTS (SELECT 1 FROM image_tags it JOIN tags t ON t.id = it.tag_id "
                        "WHERE it.image_id = i.id AND t.category_id = ? AND t.name = ?)"
                    )
                    params.extend([cid, name])

        sql = "SELECT DISTINCT i.* FROM images i WHERE " + " AND ".join(where_parts)
        sql += " ORDER BY i.created_at DESC"
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_image(r) for r in rows]


# ============================================================
# 模块级单例实例
# ============================================================

categories = CategoryRepository()
tags = TagRepository()
images = ImageRepository()
image_tags = ImageTagRepository()
search = SearchRepository()

def reconnect_image(self, image_id: int, new_path: Path) -> Image | None:
        """重新连接图片文件（文件被移动/重命名后）.

        :param image_id: 图片 ID
        :param new_path: 新的文件路径
        :return: 更新后的 Image 对象，如果图片不存在则返回 None
        """
        image = images.get_by_id(image_id)
        if not image:
            logger.warning(f"重新连接图片失败: 图片不存在 id={image_id}")
            return None
        if not new_path.exists() or not new_path.is_file():
            raise FileNotFoundError(f"文件不存在: {new_path}")

        # 重新计算哈希、尺寸等信息
        file_hash = hash_service.compute_sha256(str(new_path))
        import PIL.Image
        f = PIL.Image.open(new_path)
        width, height = f.size
        f.close()

        image.file_path = str(new_path)
        image.file_hash = file_hash
        image.file_name = new_path.name
        image.file_size = new_path.stat().st_size
        image.width = width
        image.height = height
        image.file_mtime = datetime.fromtimestamp(new_path.stat().st_mtime)
        image.is_missing = False

        images.update(image)
        # 重新生成缩略图
        thumbnail_service.ensure_thumbnail(image.id, new_path)
        logger.info(f"重新连接图片: id={image_id}, new_path={new_path}")
        return image