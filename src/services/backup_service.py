import shutil
from datetime import datetime
from pathlib import Path
from src.database import get_db
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BackupService:
    def backup(self, target_path: str | Path) -> Path:
        """将数据库备份到指定路径。"""
        target = Path(target_path)
        db = get_db()
        db_path = Path(db.db_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(db_path, target)
        logger.info(f"数据库备份完成: {target}")
        return target

    def restore(self, source_path: str | Path) -> None:
        """从备份文件恢复数据库。"""
        source = Path(source_path)
        db = get_db()
        db_path = Path(db.db_path)
        db.close()  # 关闭连接
        shutil.copy2(source, db_path)
        db.reconnect()  # 重新连接
        logger.info(f"数据库恢复完成: {source}")

backup_service = BackupService()