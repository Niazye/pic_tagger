"""
哈希服务类，提供文件哈希计算相关的业务逻辑。
"""

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
        return sha256_hash.hexdigest()


# 模块级单例实例
hash_service = HashService()