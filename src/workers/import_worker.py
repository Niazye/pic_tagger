from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
from src.utils.exception import ImageExistError
from src.utils.logger import get_logger
from src.services import image_service

logger = get_logger(__name__)

class ImportWorker(QThread):
    progress = pyqtSignal(int, int) # 进度信号，参数为当前进度和总进度
    image_imported = pyqtSignal(object) # 图片导入完成信号，参数为导入的 Image 对象
    conflict = pyqtSignal(str, str) # 冲突信号，参数为文件路径和哈希
    finished = pyqtSignal(int, int, list) # 完成信号，参数为成功数、失败数和失败原因列表

    def __init__(self, paths: list[Path], parent=None):
        super().__init__(parent)
        self.paths = paths

    def run(self):
        total = len(self.paths)
        success_count = 0
        failure_count = 0
        failures = []  # 收集失败原因
        for index, path in enumerate(self.paths, start = 1):
            self.progress.emit(index, total)
            try:
                image = image_service.add_image(Path(path))
                if image:
                    self.image_imported.emit(image)
                    success_count += 1
                    logger.info(f"导入成功: {path}")
            except ImageExistError as e:
                self.conflict.emit(str(path), str(e))
                failure_count += 1
                failures.append(f"已存在: {path.name}")
                logger.warning(f"图片已存在；跳过: {path}")
            except Exception as e:
                logger.error(f"导入图片失败: {path}, 错误: {e}", exc_info=True)
                failure_count += 1
                failures.append(f"{path.name}: {e}")
        logger.info(f"导入完成: 成功 {success_count} 张，失败 {failure_count} 张")
        self.finished.emit(success_count, failure_count, failures)
