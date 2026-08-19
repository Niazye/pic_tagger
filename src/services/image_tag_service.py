from src.database import image_tags
from src.models.image_tag import ImageTag
from src.models.tag import Tag
from src.models.image import Image
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ImageTagService:
    def add_tag_to_image(self, image_id: int, tag_id: int) -> None:
        """为图片添加标签

        :param image_id: 图片 ID
        :param tag_id: 标签 ID
        """
        image_tags.add(image_id=image_id, tag_id=tag_id)
        logger.info(f"为图片添加标签: image_id={image_id}, tag_id={tag_id}")

    def remove_tag_from_image(self, image_id: int, tag_id: int) -> None:
        """从图片中移除标签

        :param image_id: 图片 ID
        :param tag_id: 标签 ID
        """
        image_tags.remove(image_id=image_id, tag_id=tag_id)
        logger.info(f"从图片移除标签: image_id={image_id}, tag_id={tag_id}")

    def get_tags_from_image(self, image_id: int) -> list[Tag]:
        """获取图片的所有标签

        :param image_id: 图片 ID
        :return: 标签对象列表
        """
        return image_tags.get_tags_from_image(image_id=image_id)

    def get_images_from_tag(self, tag_id: int) -> list[Image]:
        """获取标签关联的所有图片

        :param tag_id: 标签 ID
        :return: 图片对象列表
        """
        return image_tags.get_images_from_tag(tag_id=tag_id)

    def batch_add_tags_to_image(self, image_id: int, tag_ids: list[int]) -> None:
        """为图片批量添加标签

        :param image_id: 图片 ID
        :param tag_ids: 标签 ID 列表
        """
        for tag_id in tag_ids:
            self.add_tag_to_image(image_id=image_id, tag_id=tag_id)
        logger.info(f"为图片批量添加标签: image_id={image_id}, tag_ids={tag_ids}")

    def get_image_tags_grouped_by_category(self, image_id: int) -> dict[int, list[Tag]]:
        """获取图片的标签，并按分类分组

        :param image_id: 图片 ID
        :return: 按分类分组的标签字典，键为分类 ID，值为标签对象列表
        """
        return image_tags.get_image_tags_grouped_by_category(image_id=image_id)

image_tag_service = ImageTagService()