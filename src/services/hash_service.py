"""
哈希服务类，提供文件哈希计算相关的业务逻辑。
"""
from src.utils.logger import get_logger

logger = get_logger(__name__)

class HashService:
    """哈希服务，计算文件的哈希值。"""
    def compute_sha256(self, file_path: str) -> str:
        """
        计算文件的 SHA-256 哈希值。
        """
        import hashlib

        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # 以块的形式读取文件，避免大文件占用过多内存
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        logger.debug(f"计算文件哈希: {file_path}, hash={file_hash[:16]}...")
        return file_hash


# 模块级单例实例
hash_service = HashService()