"""ImageTagService 单元测试。"""

from src.services import image_tag_service
from src.database.repository import categories, tags, images
from src.models.image import Image
import pytest


@pytest.fixture
def category(db):
    """创建一个测试分类。"""
    return categories.create(name="测试分类")


@pytest.fixture
def tag(category):
    """创建一个测试标签。"""
    return tags.create(category_id=category.id, name="标签A")


@pytest.fixture
def image(db):
    """创建一个测试图片记录。"""
    img = Image(file_path="/tmp/test.png", file_hash="abc123", file_name="test.png")
    return images.create(img)


def test_add_tag_to_image(image, tag):
    """为图片添加标签后，应能通过图片查询到该标签。"""
    image_tag_service.add_tag_to_image(image.id, tag.id)

    tags_from_image = image_tag_service.get_tags_from_image(image.id)
    assert len(tags_from_image) == 1
    assert tags_from_image[0].id == tag.id


def test_add_duplicate_tag_to_image(image, tag):
    """重复添加同一标签应被忽略（不产生重复关联）。"""
    image_tag_service.add_tag_to_image(image.id, tag.id)
    image_tag_service.add_tag_to_image(image.id, tag.id)

    tags_from_image = image_tag_service.get_tags_from_image(image.id)
    assert len(tags_from_image) == 1


def test_remove_tag_from_image(image, tag):
    """从图片移除标签后，图片不再关联该标签。"""
    image_tag_service.add_tag_to_image(image.id, tag.id)
    image_tag_service.remove_tag_from_image(image.id, tag.id)

    tags_from_image = image_tag_service.get_tags_from_image(image.id)
    assert len(tags_from_image) == 0


def test_get_images_from_tag(image, tag):
    """通过标签应能查询到关联的图片。"""
    image_tag_service.add_tag_to_image(image.id, tag.id)

    images_from_tag = image_tag_service.get_images_from_tag(tag.id)
    assert len(images_from_tag) == 1
    assert images_from_tag[0].id == image.id


def test_batch_add_tags_to_image(image, category):
    """批量添加多个标签。"""
    tag1 = tags.create(category_id=category.id, name="标签1")
    tag2 = tags.create(category_id=category.id, name="标签2")

    image_tag_service.batch_add_tags_to_image(image.id, [tag1.id, tag2.id])

    tags_from_image = image_tag_service.get_tags_from_image(image.id)
    assert len(tags_from_image) == 2


def test_get_image_tags_grouped_by_category(image, category):
    """按分类分组获取图片标签。"""
    tag1 = tags.create(category_id=category.id, name="标签1")
    image_tag_service.add_tag_to_image(image.id, tag1.id)

    grouped = image_tag_service.get_image_tags_grouped_by_category(image.id)
    assert category.id in grouped
    assert len(grouped[category.id]) == 1
    assert grouped[category.id][0].id == tag1.id


if __name__ == "__main__":
    pytest.main([__file__])