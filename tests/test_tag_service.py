"""TagService 单元测试。"""

from src.services import tag_service
from src.database.repository import categories, tags
import pytest


@pytest.fixture
def category(db):
    """创建一个测试分类。"""
    return categories.create(name="测试分类")


def test_add_tag(category):
    """添加标签后应返回带 id 的标签对象。"""
    tag = tag_service.add_tag(category.id, "标签A")
    assert tag.id is not None
    assert tag.name == "标签A"
    assert tag.category_id == category.id

    fetched = tags.get_by_id(tag.id)
    assert fetched is not None
    assert fetched.name == "标签A"


def test_add_tag_with_url(category):
    """添加带链接的标签。"""
    tag = tag_service.add_tag(category.id, "标签A", url="https://example.com")
    assert tag.url == "https://example.com"


def test_rename_tag(category):
    """重命名标签。"""
    tag = tag_service.add_tag(category.id, "旧名")
    renamed = tag_service.rename_tag(tag.id, "新名")
    assert renamed is not None
    assert renamed.name == "新名"

    fetched = tags.get_by_id(tag.id)
    assert fetched.name == "新名"


def test_rename_nonexistent_tag(category):
    """重命名不存在的标签应返回 None。"""
    assert tag_service.rename_tag(9999, "新名") is None


def test_delete_tag(category):
    """删除标签。"""
    tag = tag_service.add_tag(category.id, "标签A")
    deleted = tag_service.delete_tag(tag.id)
    assert deleted is not None
    assert deleted.id == tag.id

    assert tags.get_by_id(tag.id) is None


def test_delete_nonexistent_tag(category):
    """删除不存在的标签应返回 None。"""
    assert tag_service.delete_tag(9999) is None


def test_get_all_tags_by_category(category):
    """获取分类下所有标签。"""
    tag_service.add_tag(category.id, "标签A")
    tag_service.add_tag(category.id, "标签B")

    result = tag_service.get_all_tags_by_category(category.id)
    names = [t.name for t in result]
    assert "标签A" in names
    assert "标签B" in names


def test_set_url(category):
    """设置标签链接。"""
    tag = tag_service.add_tag(category.id, "标签A")
    updated = tag_service.set_url(tag.id, "https://example.com")
    assert updated is not None
    assert updated.url == "https://example.com"

    fetched = tags.get_by_id(tag.id)
    assert fetched.url == "https://example.com"


def test_set_url_nonexistent(category):
    """设置不存在标签的链接应返回 None。"""
    assert tag_service.set_url(9999, "https://example.com") is None


def test_set_url_empty(category):
    """设置空链接应返回 None。"""
    tag = tag_service.add_tag(category.id, "标签A")
    assert tag_service.set_url(tag.id, "") is None


if __name__ == "__main__":
    pytest.main([__file__])