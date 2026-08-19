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

    def update_description(self, image_id: int, description:str) -> Image | None:
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
        image.description = description
        images.update(image)
        logger.info(f"更新图片描述: id={image_id}, description={description}")
        return image
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

# 模块级单例实例
image_service = ImageService()