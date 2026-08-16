"""pytest 共享 fixture 定义。"""

import pytest
from pathlib import Path

# 测试目录路径
TESTS_DIR = Path(__file__).parent
@pytest.fixture
def default_thumbnail_path() -> Path:
    """返回默认缩略图路径（default.png）。"""
    return (TESTS_DIR / "default.png")

@pytest.fixture
def tmp_filepath() -> str:
    """返回测试图片路径（test_pic1.png）。"""
    return str(TESTS_DIR / "test_pic1.png")


@pytest.fixture
def tmp_filepath_2() -> str:
    """返回另一张测试图片路径（test_pic2.png）。"""
    return str(TESTS_DIR / "test_pic2.png")


@pytest.fixture
def tmp_filepath_copy() -> str:
    """返回 test_pic1.png 的副本（内容相同，用于测试哈希一致性）。"""
    return str(TESTS_DIR / "test_pic1_copy.png")