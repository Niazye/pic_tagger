"""标签模型。"""

from dataclasses import dataclass


@dataclass
class Tag:
    """标签。

    url 为可选超链接（P4 功能预留）。
    """

    id: int | None = None
    category_id: int = 0
    name: str = ""
    url: str | None = None