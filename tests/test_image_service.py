"""ImageService 单元测试。"""

from src.services import image_service, thumbnail_service
from src.database.repository import images
from src.utils.exception import ImageExistError
from pathlib import Path
import shutil
import pytest


def _cleanup_thumbnail(image_id: int) -> None:
    """清理测试过程中生成的缩略图，避免污染真实缓存目录。"""
    thumbnail_path = thumbnail_service.get_thumbnail_path(image_id)
    if thumbnail_path.exists():
        thumbnail_path.unlink()


def test_add_image(tmp_filepath, db):
    """添加图片后应返回带 id 的 Image 对象，且能通过 id 查询到。"""
    image = image_service.add_image(Path(tmp_filepath))
    assert image is not None
    assert image.id is not None
    assert image.file_name == Path(tmp_filepath).name
    assert image.width is not None and image.width > 0
    assert image.height is not None and image.height > 0

    fetched = images.get_by_id(image.id)
    assert fetched is not None
    assert fetched.file_path == str(Path(tmp_filepath))

    _cleanup_thumbnail(image.id)


def test_add_image_nonexistent(db):
    """添加不存在的文件应抛出 FileNotFoundError。"""
    with pytest.raises(FileNotFoundError):
        image_service.add_image(Path("non_existent.png"))


def test_add_duplicate_image(tmp_filepath, db):
    """重复添加相同内容的图片应抛出 ImageExistError。"""
    image = image_service.add_image(Path(tmp_filepath))
    with pytest.raises(ImageExistError):
        image_service.add_image(Path(tmp_filepath))
    _cleanup_thumbnail(image.id)


def test_add_duplicate_by_copy(tmp_filepath, tmp_filepath_copy, db):
    """添加内容相同的副本也应被去重。"""
    image = image_service.add_image(Path(tmp_filepath))
    with pytest.raises(ImageExistError):
        image_service.add_image(Path(tmp_filepath_copy))
    _cleanup_thumbnail(image.id)


def test_remove_image(tmp_filepath, db):
    """删除图片后，数据库中不应再存在该图片。"""
    image = image_service.add_image(Path(tmp_filepath))
    removed = image_service.remove_image(image.id)
    assert removed is not None
    assert removed.id == image.id

    assert images.get_by_id(image.id) is None
    _cleanup_thumbnail(image.id)


def test_remove_nonexistent_image(db):
    """删除不存在的图片应返回 None。"""
    assert image_service.remove_image(9999) is None


def test_remove_image_with_delete_file(tmp_filepath, tmp_path, db):
    """删除图片并删除原始文件。"""
    # 复制一份测试图片到临时目录，避免删除测试资源
    src = Path(tmp_filepath)
    dst = tmp_path / "to_delete.png"
    shutil.copy(src, dst)

    image = image_service.add_image(dst)
    image_service.remove_image(image.id, delete_file=True)

    assert not dst.exists(), "原始文件应被删除"
    _cleanup_thumbnail(image.id)


if __name__ == "__main__":
    pytest.main([__file__])