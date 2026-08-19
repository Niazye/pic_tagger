from src.database.repository import tags
from src.models.tag import Tag
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TagService:
    def add_tag(self, category_id: int, name: str, url: str | None = None) -> Tag:
        """添加一个新的标签

        :param category_id: 分类 ID
        :param name: 标签名称
        :param url: 标签链接，可选
        :return: 创建的标签对象
        """
        tag = tags.create(category_id=category_id, name=name, url=url)
        logger.info(f"创建标签: id={tag.id}, category_id={category_id}, name={name}")
        return tag

    def rename_tag(self, tag_id: int, new_name: str) -> Tag | None:
        """重命名一个标签

        :param tag_id: 标签 ID
        :param new_name: 新的标签名称
        :return: 更新后的标签对象，如果标签不存在则返回 None
        """
        tag = tags.get_by_id(tag_id)
        if not tag:
            logger.warning(f"重命名标签失败: 标签不存在 id={tag_id}")
            return None
        old_name = tag.name
        tag.name = new_name
        tags.rename(tag_id, new_name)
        logger.info(f"重命名标签: id={tag_id}, {old_name} -> {new_name}")
        return tag

    def delete_tag(self, tag_id: int) -> Tag | None:
        """删除一个标签

        :param tag_id: 标签 ID
        :return: 被删除的标签对象，如果标签不存在则返回 None
        """
        tag = tags.get_by_id(tag_id)
        if not tag:
            logger.warning(f"删除标签失败: 标签不存在 id={tag_id}")
            return None
        tags.delete(tag_id)
        logger.info(f"删除标签: id={tag_id}, name={tag.name}")
        return tag

    def get_all_tags_by_category(self, category_id: int) -> list[Tag]:
        """获取指定分类下的所有标签

        :param category_id: 分类 ID
        :return: 标签对象列表
        """
        return tags.get_by_category(category_id)

    def set_url(self, tag_id: int, url: str | None) -> Tag | None:
        """设置标签的链接

        :param tag_id: 标签 ID
        :param url: 标签链接，可选
        :return: 更新后的标签对象，如果标签不存在则返回 None
        """
        tag = tags.get_by_id(tag_id)
        if not tag or not url:
            logger.warning(f"设置标签链接失败: 标签不存在或链接为空 id={tag_id}")
            return None
        tag.url = url
        tags.set_url(tag_id, url)
        logger.info(f"设置标签链接: id={tag_id}, url={url}")
        return tag

    def autocomplete_tags(self, prefix: str, limit: int = 10) -> list[Tag]:
        """具有模糊搜索功能的标签自动补全
        """
        raise NotImplementedError("标签自动补全功能尚未实现")


tag_service = TagService()