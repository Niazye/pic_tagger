"""
缩略图服务。
"""

from PIL import Image, UnidentifiedImageError
from pathlib import Path
from src.utils.path import get_thumbnail_dir, get_assets_dir, ensure_dirs
from src.utils.exception import NoThumbnailError
from src.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_THUMBNAIL = "default.png"

class ThumbnailService:
    def generate_thumbnail(self, image_path: Path, image_id: int, size=(200, 200)) -> Path:
        """
        生成缩略图。

        :param image_path: 原始图片路径
        :param image_id: 图片 ID，用于生成缩略图文件名
        :param size: 缩略图尺寸，默认为 (200, 200)
        :return: 缩略图路径；若图片不可用，返回默认缩略图路径
        """
        file_name = f"{image_id}.png"
        thumbnail_path = get_thumbnail_dir() / file_name
        try:
            ensure_dirs()
            with Image.open(image_path) as img:
                img.thumbnail(size)
                img.save(thumbnail_path, "PNG")
            logger.info(f"生成缩略图: image_id={image_id}, path={thumbnail_path}")
            return thumbnail_path
        except (FileNotFoundError, UnidentifiedImageError, OSError) as e:
            logger.error(f"生成缩略图失败: image_id={image_id}, path={image_path}, 错误: {e}")
            raise NoThumbnailError(f"无法生成缩略图: {image_path}")

    def get_thumbnail_path(self, image_id: int) -> Path:
        return get_thumbnail_dir() / f"{image_id}.png"

    def get_default_thumbnail_path(self) -> Path:
        """返回默认缩略图路径（图片不可用时的占位图）。"""
        return get_assets_dir() / DEFAULT_THUMBNAIL

    def remove_thumbnail(self, image_id: int):
        """
        删除指定图片 ID 的缩略图。

        :param image_id: 图片 ID
        """
        thumbnail_path = self.get_thumbnail_path(image_id)
        if thumbnail_path.exists():
            thumbnail_path.unlink()
            logger.info(f"删除缩略图: image_id={image_id}, path={thumbnail_path}")
        else:
            logger.warning(f"删除缩略图失败: 缩略图不存在 image_id={image_id}")
            raise NoThumbnailError(f"缩略图不存在: {thumbnail_path}")

    def ensure_thumbnail(self, image_id: int, image_path: Path, size=(200, 200)) -> Path:
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
        count = 0
        for thumbnail_file in thumbnail_dir.glob("*.png"):
            thumbnail_file.unlink()
            count += 1
        logger.info(f"清空缩略图缓存: 共删除 {count} 个文件")


# 模块级单例实例
thumbnail_service = ThumbnailService()