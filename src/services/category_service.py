from src.models.category import Category
from src.database.repository import categories, tags
from src.database.schema import DEFAULT_CATEGORY_ID
from src.utils.exception import DefaultCategoryError

class CategoryService:
    """分类服务"""
    def create_category(self, name: str, type: str = 'free') -> Category:
        """创建一个新的分类

        :param name: 分类名称
        :return: 创建的分类对象
        """
        return categories.create(name=name, category_type=type)

    def rename_category(self, category_id: int, new_name: str) -> Category | None:
        """重命名一个分类

        :param category_id: 分类 ID
        :param new_name: 新的分类名称
        :return: 更新后的分类对象，如果分类不存在则返回 None
        """
        category = categories.get_by_id(category_id)
        if not category:
            return None
        # 默认分类不允许重命名
        if category.id == DEFAULT_CATEGORY_ID:
            raise DefaultCategoryError("默认分类不允许重命名")
        category.name = new_name
        categories.rename(category_id, new_name)
        return category

    def delete_category(self, category_id: int, mode: str = "move_to_default") -> Category | None:
        """删除一个分类

        :param category_id: 分类 ID
        :param mode: 删除模式，默认为 "move_to_default"，表示将该分类下的标签移动到默认分类；如果为 "delete_tags"，则删除该分类下的所有标签。
        :return: 被删除的分类对象，如果分类不存在则返回 None；默认分类不允许删除，同样返回 None。
        """
        category = categories.get_by_id(category_id)
        if not category:
            return None
        # 默认分类不允许删除
        if category.id == DEFAULT_CATEGORY_ID:
            raise DefaultCategoryError("默认分类不允许删除")
        if mode == "move_to_default":
            # 默认分类在数据库初始化时已自动创建，通过固定 id 直接获取
            default_category = categories.get_by_id(DEFAULT_CATEGORY_ID)
            assert default_category is not None and default_category.id is not None
            # 将该分类下的所有标签迁移到默认分类
            for tag in tags.get_by_category(category_id):
                assert tag.id is not None
                tags.move_to_category(tag.id, default_category.id)
        categories.delete(category_id)
        return category

    def set_color(self, category_id: int, color_hex: str) -> Category | None:
        """设置分类的颜色

        :param category_id: 分类 ID
        :param color_hex: 颜色的十六进制表示，例如 "#FF5733"
        :return: 更新后的分类对象，如果分类不存在则返回 None
        """
        category = categories.get_by_id(category_id)
        if not category:
            return None
        category.color_hex = color_hex
        categories.set_color(category_id, color_hex)
        return category

    def get_all_categories(self) -> list[Category]:
        """获取所有分类

        :return: 分类对象列表
        """
        return categories.get_all()


category_service = CategoryService()