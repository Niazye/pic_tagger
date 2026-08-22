from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QFileDialog, QMessageBox
from src.views import ToolBar, DetailTableView, DetailPanel
from src.controllers import ImportController
from PyQt6.QtCore import Qt
from pathlib import Path
from src.utils.logger import get_logger
from src.services.image_service import image_service

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

        # 详情区
        self.detail_panel = DetailPanel(self)
        layout.addWidget(self.detail_panel, 3)

        self.setCentralWidget(central_widget)

        # 连接信号        
        self.detail_table_view.itemSelectionChanged.connect(self._on_selection_changed)
        self.detail_panel.tags_changed.connect(self._on_tags_changed)
        self.detail_table_view.refresh()  # 初始化时刷新详情表格
    def _on_delete_images(self, image_ids: list[int]):
        """处理删除图片索引的请求。

        :param image_ids: 要删除的图片 ID 列表
        """
        if not image_ids:
            return

        # 弹出确认对话框
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(image_ids)} 张图片的索引吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        for image_id in image_ids:
            image_service.remove_image(image_id, delete_file=False)
        self._refresh_all()
        logger.info(f"删除图片索引: {len(image_ids)} 张图片的索引已删除")

    def _refresh_all(self):
        self.detail_table_view.refresh()

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

    def _on_tags_changed(self):
        """当标签发生变化时，刷新详情表格和文件列表。"""
        self.detail_table_view.refresh()

    def _on_selection_changed(self):
        """当选中图片发生变化时，更新详情面板的显示。

        """
        # 获取当前选中的图片
        selected = self.detail_table_view.selectedItems()
        if not selected:
            self.detail_panel.clear()
            return
        # 获取选中行的id
        rows = set()
        for item in selected:
            rows.add(item.row())
        ids = []
        for row in rows:
            name_item = self.detail_table_view.item(row, 0)
            if name_item:
                image_id = name_item.data(Qt.ItemDataRole.UserRole)
                if image_id is not None:
                    ids.append(image_id)
        if len(ids) == 1:
            image = image_service.get_image_by_id(ids[0])
            if image:
                self.detail_panel.show_image(image)
        elif len(ids) > 1:
            self.detail_panel.show_multi(ids)
        else:
            self.detail_panel.clear()