from src.services import hash_service

import pytest

def test_same_file(tmp_filepath):
    test_file = tmp_filepath

    # 计算哈希值
    computed_hash = hash_service.compute_sha256(test_file)
    repeated_hash = hash_service.compute_sha256(test_file)

    assert computed_hash == repeated_hash, "哈希值不一致，可能存在计算错误。"

def test_different_files(tmp_filepath, tmp_filepath_2):
    if tmp_filepath == tmp_filepath_2:
        # 如果两个文件路径相同，跳过测试
        return
    hash1 = hash_service.compute_sha256(tmp_filepath)
    hash2 = hash_service.compute_sha256(tmp_filepath_2)

    assert hash1 != hash2, "不同文件的哈希值不应相同，可能存在计算错误。"

def test_nonexistent_file():
    try:
        hash_service.compute_sha256("non_existent_file.txt")
    except FileNotFoundError:
        pass  # 预期的异常
    else:
        assert False, "预期 FileNotFoundError 异常，但未抛出。"

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])