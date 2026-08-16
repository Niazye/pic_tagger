from src.services import thumbnail_service
from src.utils.exception import NoThumbnailError
import pytest

def test_generate_thumbnail(tmp_filepath):
    image_id = "test_id"
    thumbnail_path = thumbnail_service.generate_thumbnail(tmp_filepath, image_id)

    # 检查生成的缩略图是否存在
    assert thumbnail_path.exists(), "缩略图未生成"

    # 检查生成的缩略图是否为 PNG 格式
    assert thumbnail_path.suffix == ".png", "缩略图格式不正确"

    # 检查缩略图尺寸：thumbnail() 是等比缩放，最长边不超过 200
    from PIL import Image
    with Image.open(thumbnail_path) as image:
        assert max(image.size) <= 200, "缩略图最长边不应超过 200"
        assert min(image.size) > 0, "缩略图尺寸无效"

    # 清理生成的缩略图
    thumbnail_path.unlink()

def test_generate_thumbnail_with_nonexistent_file():
    image_id = "nonexistent_id"

    # 不存在的文件应抛出异常
    with pytest.raises(NoThumbnailError):
        thumbnail_service.generate_thumbnail("non_existent_file.png", image_id)

def test_ensure_thumbnail(tmp_filepath, tmp_filepath_2):
    image_id = "ensure_test_id"

    # 调用 ensure_thumbnail 方法
    ensured_thumbnail_path = thumbnail_service.ensure_thumbnail(image_id, tmp_filepath)

    # 检查生成的缩略图是否存在
    assert ensured_thumbnail_path.exists(), "缩略图未生成"

    # 检查生成的缩略图是否为 PNG 格式
    assert ensured_thumbnail_path.suffix == ".png", "缩略图格式不正确"

    # 重复调用不重复生成（只检查当前 image_id 的缩略图，避免受其他测试残留影响）
    for _ in range(4):
        thumbnail_service.ensure_thumbnail(image_id, tmp_filepath)
    assert ensured_thumbnail_path.exists(), "重复调用 ensure_thumbnail 后缩略图应仍存在"

    # 清理生成的缩略图
    ensured_thumbnail_path.unlink()

def test_clear_thumbnails(tmp_filepath):
    # 生成数个缩略图
    for i in range(5):
        image_id = f"clear_test_id_{i}"
        thumbnail_path = thumbnail_service.get_thumbnail_path(image_id)
        thumbnail_service.generate_thumbnail(tmp_filepath, image_id)
        assert thumbnail_path.exists(), "缩略图未生成"

    # 清空所有缩略图
    thumbnail_service.clear_thumbnails()

    # 检查缩略图是否已被删除
    assert not thumbnail_path.exists(), "缩略图未被清除"

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])