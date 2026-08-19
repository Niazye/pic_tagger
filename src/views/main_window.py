from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QFileDialog
from src.views import ToolBar, DetailTableView
from src.controllers import ImportController
from PyQt6.QtCore import Qt
from pathlib import Path
from src.utils.logger import get_logger

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PicTagger")
        self.resize(1200,800)

        self.toolbar = ToolBar(self)
        self.addToolBar(self.toolbar)

        # 导入控制器
        self.import_controller = ImportController(self)
        self.import_controller.import_finished.connect(self._on_import_finished)
        self.toolbar.import_button.clicked.connect(self._on_import_clicked)

        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.detail_table_view = DetailTableView(self)

        self.middle_container = QWidget()
        middle_layout = QHBoxLayout(self.middle_container)
        middle_layout.setContentsMargins(0,0,0,0)
        middle_layout.setSpacing(0)
        middle_layout.addWidget(self.detail_table_view)
        layout.addWidget(self.middle_container, 7)

        self.datail_placeholder = QLabel("详情区")
        self.datail_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.datail_placeholder.setStyleSheet("background-color: #e0e0e0; border: 1px solid #ccc;")
        layout.addWidget(self.datail_placeholder, 3)

        self.setCentralWidget(central_widget)

        self.detail_table_view.refresh()  # 初始化时刷新详情表格

    def _on_import_clicked(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "选择图片文件",
            filter=f"图片文件 ({'*'+' *'.join(self.import_controller.IMAGE_EXTENSIONS)})"
        )
        if paths:
            self.import_controller.import_files([Path(p) for p in paths])

    def _on_import_finished(self, success_count: int, failure_count: int):
        self.detail_table_view.refresh()
        logger.info(f"导入完成: 成功 {success_count} 张，失败 {failure_count} 张")