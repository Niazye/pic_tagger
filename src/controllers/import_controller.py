from pathlib import Path
from src.services.image_service import image_service
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QMainWindow
from src.models.image import Image
from src.workers.import_worker import ImportWorker
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ImportController(QObject):
    import_finished = pyqtSignal(int, int)  # 完成信号，参数为成功数和失败数

    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__(parent)
        self.worker = None

    def import_files(self, paths: list[Path]) -> None:
        logger.info(f"开始导入 {len(paths)} 个文件")
        self._start_import(paths)

    def import_folder(self, folder_path: Path) -> None:
        paths = [
            p for p in folder_path.rglob('*') if p.is_file() and p.suffix.lower() in self.IMAGE_EXTENSIONS
        ]
        logger.info(f"开始导入文件夹 {folder_path}，共找到 {len(paths)} 个图片文件")
        self._start_import(paths)

    def _start_import(self, paths: list[Path]) -> None:
        if not paths:
            logger.warning("没有文件可导入")
            self.import_finished.emit(0, 0)
            return
        self.worker = ImportWorker(paths)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, success_count: int, failure_count: int) -> None:
        self.worker = None
        self.import_finished.emit(success_count, failure_count)