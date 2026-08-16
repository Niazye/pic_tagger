"""图片模型。"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Image:
    """图片索引。

    is_missing 标记文件是否丢失（0=正常，1=丢失）。
    """

    id: int = 0
    file_path: str = ""
    file_hash: str = ""
    file_name: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    file_size: int | None = None
    width: int | None = None
    height: int | None = None
    file_mtime: datetime | None = None
    is_missing: int = 0