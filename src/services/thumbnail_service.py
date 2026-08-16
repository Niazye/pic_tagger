"""
缩略图服务。
"""

from PIL import Image, UnidentifiedImageError
from pathlib import Path
from utils.path import get_thumbnail_dir, get_assets_dir

DEFAULT_THUMBNAIL = "default.png"

class ThumbnailService:
    def generate_thumbnail(self, image_path: Path, image_id: str, size=(200, 200)) -> Path:
        """
        生成缩略图。

        :param image_path: 原始图片路径
        :param image_id: 图片 ID，用于生成缩略图文件名
        :param size: 缩略图尺寸，默认为 (200, 200)
        :return: 缩略图路径；若图片不可用，返回默认缩略图路径
        """
        file_name = f"{image_id}.jpg"
        thumbnail_path = get_thumbnail_dir() / file_name
        try:
            with Image.open(image_path) as img:
                img.thumbnail(size)
                img.save(thumbnail_path, "JPEG")
            return thumbnail_path
        except (FileNotFoundError, UnidentifiedImageError, OSError):
            # 图片不存在、损坏或无法解析时，使用默认缩略图
            return self.get_default_thumbnail_path()

    def get_thumbnail_path(self, image_id) -> Path:
        return get_thumbnail_dir() / f"{image_id}.jpg"

    def get_default_thumbnail_path(self) -> Path:
        """返回默认缩略图路径（图片不可用时的占位图）。"""
        return get_assets_dir() / DEFAULT_THUMBNAIL

    def ensure_thumbnail(self, image_id: str, image_path: Path, size=(200, 200)) -> Path:
        """
        确保缩略图存在，如果不存在则生成。

        :param image_path: 原始图片路径
        :param image_id: 图片 ID，用于生成缩略图文件名
        :param size: 缩略图尺寸，默认为 (200, 200)
        :return: 缩略图路径；若图片不可用，返回默认缩略图路径
        """
        thumbnail_path = self.get_thumbnail_path(image_id)
        if not thumbnail_path.exists():
            return self.generate_thumbnail(image_path, image_id, size)
        return thumbnail_path

    def clear_thumbnails(self):
        """
        清空所有缩略图缓存。
        """
        thumbnail_dir = get_thumbnail_dir()
        for thumbnail_file in thumbnail_dir.glob("*.jpg"):
            thumbnail_file.unlink()