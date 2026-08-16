"""分类模型。"""

from dataclasses import dataclass, field


@dataclass
class Category:
    """标签分类。

    category_type:
        - 'free'   自由式（默认）：可自由输入新标签
        - 'option' 选项式：只能从已有标签中选择
        - 'unique' 唯一式：每张图片该分类下只能有一个标签
    """

    id: int | None = None
    name: str = ""
    color_hex: str | None = None
    sort_order: int = 0
    category_type: str = "free"

    def __post_init__(self):
        if self.category_type not in ("free", "option", "unique"):
            raise ValueError(f"无效的分类类型: {self.category_type}")