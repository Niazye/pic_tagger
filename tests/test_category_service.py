"""CategoryService 单元测试。"""

from src.services import category_service
from src.database.repository import categories, tags
from src.database.schema import DEFAULT_CATEGORY_ID, DEFAULT_CATEGORY_NAME
from src.utils.exception import DefaultCategoryError
import pytest


def test_create_category(db):
    """创建分类后应返回带 id 的分类对象，且能通过 id 查询到。"""
    category = category_service.create_category("人物")
    assert category.id is not None
    assert category.name == "人物"
    assert category.category_type == "free"

    # 从数据库重新读取，验证已持久化
    fetched = categories.get_by_id(category.id)
    assert fetched is not None
    assert fetched.name == "人物"


def test_create_category_with_type(db):
    """创建 option 类型分类。"""
    category = category_service.create_category("评分", type="option")
    assert category.category_type == "option"


def test_rename_category(db):
    """重命名分类后，名称应更新。"""
    category = category_service.create_category("旧名")
    renamed = category_service.rename_category(category.id, "新名")
    assert renamed is not None
    assert renamed.name == "新名"

    fetched = categories.get_by_id(category.id)
    assert fetched.name == "新名"


def test_rename_nonexistent_category(db):
    """重命名不存在的分类应返回 None。"""
    assert category_service.rename_category(9999, "新名") is None


def test_rename_default_category_raises(db):
    """默认分类不允许重命名。"""
    with pytest.raises(DefaultCategoryError):
        category_service.rename_category(DEFAULT_CATEGORY_ID, "改名")


def test_delete_category_move_to_default(db):
    """删除分类（move_to_default）后，其下标签应迁移到默认分类。"""
    category = category_service.create_category("临时")
    tag = tags.create(category_id=category.id, name="标签A")

    deleted = category_service.delete_category(category.id, mode="move_to_default")
    assert deleted is not None
    assert deleted.id == category.id

    # 标签应迁移到默认分类
    moved = tags.get_by_id(tag.id)
    assert moved is not None
    assert moved.category_id == DEFAULT_CATEGORY_ID


def test_delete_category_delete_tags(db):
    """删除分类（delete_tags）后，其下标签应被删除。"""
    category = category_service.create_category("临时")
    tag = tags.create(category_id=category.id, name="标签A")

    category_service.delete_category(category.id, mode="delete_tags")

    # 标签应被删除
    assert tags.get_by_id(tag.id) is None


def test_delete_nonexistent_category(db):
    """删除不存在的分类应返回 None。"""
    assert category_service.delete_category(9999) is None


def test_delete_default_category_raises(db):
    """默认分类不允许删除。"""
    with pytest.raises(DefaultCategoryError):
        category_service.delete_category(DEFAULT_CATEGORY_ID)


def test_set_color(db):
    """设置分类颜色。"""
    category = category_service.create_category("人物")
    updated = category_service.set_color(category.id, "#FF5733")
    assert updated is not None
    assert updated.color_hex == "#FF5733"

    fetched = categories.get_by_id(category.id)
    assert fetched.color_hex == "#FF5733"


def test_set_color_nonexistent(db):
    """设置不存在分类的颜色应返回 None。"""
    assert category_service.set_color(9999, "#FF5733") is None


def test_get_all_categories_includes_default(db):
    """获取所有分类应包含默认分类。"""
    categories_list = category_service.get_all_categories()
    names = [c.name for c in categories_list]
    assert DEFAULT_CATEGORY_NAME in names


if __name__ == "__main__":
    pytest.main([__file__])