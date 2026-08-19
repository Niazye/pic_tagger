from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
from src.utils.exception import ImageExistError
from src.services.image_service import image_service

class ImportWorker(QThread):
    progress = pyqtSignal(int, int) # 进度信号，参数为当前进度和总进度
    image_imported = pyqtSignal(object) # 图片导入完成信号，参数为导入的 Image 对象
    conflict = pyqtSignal(str, str) # 冲突信号，参数为文件路径和哈希
    finished = pyqtSignal(int, int) # 完成信号，参数为成功数和失败数

    def __init__(self, paths: list[Path], parent=None):
        super().__init__(parent)
        self.paths = paths

    def run(self):
        total = len(self.paths)
        success_count = 0
        failure_count = 0
        for index, path in enumerate(self.paths, start = 1):
            self.progress.emit(index, total)
            try:
                image = image_service.add_image(Path(path))
                if image:
                    self.image_imported.emit(image)
                    success_count += 1
            except ImageExistError as e:
                self.conflict.emit(path, str(e))
                failure_count += 1
            except Exception as e:
                print(f"导入图片失败: {path}, 错误: {e}")
                failure_count += 1
        self.finished.emit(success_count, failure_count)
