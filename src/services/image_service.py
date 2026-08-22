"""
图片服务
"""
from pathlib import Path
from src.services import hash_service, thumbnail_service
from src.models import Image
from src.database import images
from datetime import datetime
from src.utils.exception import ImageExistError
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ImageService:
    def add_image(self, path: Path) -> Image | None:
        """
        添加图片到数据库。

        :param path: 图片文件路径
        :return: Image 对象，如果添加失败则返回 None
        """
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"文件不存在: {path}")

        file_hash = hash_service.compute_sha256(str(path))
        if images.get_by_hash(file_hash):
            # 如果数据库中已经存在该图片
            raise ImageExistError(f"图片已导入: {path}")
        import PIL.Image
        f = PIL.Image.open(path)
        width, height = f.size
        f.close()
        image = Image(
            file_path=str(path),
            file_hash=file_hash,
            file_name=path.name,
            file_size=path.stat().st_size,
            width=width,
            height=height,
            file_mtime=datetime.fromtimestamp(path.stat().st_mtime),
        )
        images.create(image)
        thumbnail_service.ensure_thumbnail(image.id, path)
        return image
    def remove_image(self, image_id: int, delete_file: bool = False) -> Image | None:
        """
        从数据库中删除图片。

        :param image_id: 图片 ID
        :return: 如果删除成功返回删除的图片对应的 Image 对象，否则返回 None
        """
        image = images.get_by_id(image_id)
        if not image:
            return None

        # 删除数据库中的图片记录
        images.delete(image_id)
        
        # 删除缩略图
        thumbnail_service.remove_thumbnail(image_id)

        # 如果需要删除原始文件
        if delete_file:
            try:
                path = Path(image.file_path)
                if path.exists():
                    path.unlink()
            except Exception as e:
                logger.error(f"删除原始文件失败: {image.file_path}, 错误: {e}", exc_info=True)
        return image

    def get_image_by_hash(self, file_hash: str) -> Image | None:
        """
        根据文件哈希获取图片。

        :param file_hash: 文件哈希
        :return: 如果找到返回对应的 Image 对象，否则返回 None
        """
        return images.get_by_hash(file_hash)

    def get_all_images(self) -> list[Image]:
        """
        获取所有图片。

        :return: 图片列表
        """
        return images.get_all()

    def get_image_by_id(self, image_id: int) -> Image | None:
        """
        根据图片 ID 获取图片。

        :param image_id: 图片 ID
        :return: 如果找到返回对应的 Image 对象，否则返回 None
        """
        return images.get_by_id(image_id)
    def update_description(self, image_id: int, description: str) -> Image | None:
        """
        更新图片的描述信息。

        :param image_id: 图片 ID
        :param description: 新的描述信息
        :return: 更新后的 Image 对象，如果图片不存在则返回 None
        """
        image = images.get_by_id(image_id)
        if not image:
            logger.warning(f"更新图片描述失败: 图片不存在 id={image_id}")
            return None
        images.update_description(image_id, description)
        image.description = description
        logger.info(f"更新图片描述: id={image_id}, description={description}")
        return image

    def reconnect_image(self, image_id: int, new_path: Path) -> Image | None:
        """重新连接图片文件（文件被移动/重命名后）。

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

        existing_image = images.get_by_hash(file_hash)
        if existing_image and existing_image.id != image_id:
            raise ImageExistError(f"图片已存在于数据库中: {new_path}")
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
        thumbnail_service.generate_thumbnail(new_path, image_id)
        logger.info(f"重新连接图片: id={image_id}, new_path={new_path}")
        return image

    def check_missing_files(self) -> int:
        """
        检查数据库中所有图片的文件是否存在，并更新 is_missing 字段。

        :return: 缺失文件的数量
        """
        missing_count = 0
        for image in self.get_all_images():
            is_missing = not Path(image.file_path).exists()
            if is_missing != bool(image.is_missing):
                self.set_missing(image.id, is_missing)
            if is_missing:
                missing_count += 1
        return missing_count

    def set_missing(self, image_id: int, is_missing: bool) -> None:
        """
        设置图片的 is_missing 字段。

        :param image_id: 图片 ID
        :param is_missing: 是否缺失
        """
        images.set_missing(image_id, is_missing)
        logger.info(f"设置图片缺失状态: id={image_id}, is_missing={is_missing}")

# 模块级单例实例
image_service = ImageService()