"""SearchService 单元测试。"""

from src.services import search_service
from src.database.repository import categories, tags, images, image_tags
from src.models.image import Image
import pytest


@pytest.fixture
def category(db):
    """创建一个测试分类。"""
    return categories.create(name="测试分类")


@pytest.fixture
def tag(category):
    """创建一个测试标签。"""
    return tags.create(category_id=category.id, name="风景")


def _create_image(file_name: str, file_hash: str) -> Image:
    """创建一个测试图片记录。"""
    img = Image(file_path=f"/tmp/{file_name}", file_hash=file_hash, file_name=file_name)
    return images.create(img)


def test_search_by_keyword_in_filename(db):
    """按文件名关键词搜索。"""
    img = _create_image("beach.png", "hash1")
    results = search_service.search_image_by_keyword("beach")
    assert any(i.id == img.id for i in results)


def test_search_by_keyword_in_tag_name(db, tag):
    """按标签名关键词搜索。"""
    img = _create_image("photo.png", "hash2")
    image_tags.add(img.id, tag.id)

    results = search_service.search_image_by_keyword("风景")
    assert any(i.id == img.id for i in results)


def test_search_by_keyword_no_match(db):
    """无匹配关键词应返回空列表。"""
    _create_image("beach.png", "hash1")
    results = search_service.search_image_by_keyword("不存在的关键词")
    assert results == []


def test_search_by_tag_keyword(db, category, tag):
    """按标签关键词搜索。"""
    img = _create_image("photo.png", "hash2")
    image_tags.add(img.id, tag.id)

    results = search_service.search_image_by_tag_keyword(category.id, "风景")
    assert any(i.id == img.id for i in results)


def test_combined_search_keyword_and_tag(db, category, tag):
    """组合搜索：关键词 + 标签条件（AND）。"""
    img = _create_image("beach.png", "hash3")
    image_tags.add(img.id, tag.id)

    results = search_service.combined_search("beach", [(category.id, "风景")])
    assert any(i.id == img.id for i in results)


def test_combined_search_empty(db):
    """无关键词且无条件应返回空列表。"""
    assert search_service.combined_search(None, None) == []


if __name__ == "__main__":
    pytest.main([__file__])