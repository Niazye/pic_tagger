"""图片-标签关联模型。"""

from dataclasses import dataclass


@dataclass
class ImageTag:
    """图片与标签的多对多关联。"""

    image_id: int = 0
    tag_id: int = 0