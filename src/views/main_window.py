from PyQt6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QFileDialog, QMessageBox
from src.views import ToolBar, DetailTableView, FileListView, DetailPanel
from src.controllers import ImportController
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from pathlib import Path
from src.utils.logger import get_logger
from src.services import image_service, search_service, backup_service
import os
import subprocess
import sys

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
        self.file_list_view = FileListView(self)
        self.file_list_view.hide()  # 默认隐藏文件列表视图，显示详情表格

        self.middle_container = QWidget()
        middle_layout = QHBoxLayout(self.middle_container)
        middle_layout.setContentsMargins(0,0,0,0)
        middle_layout.setSpacing(0)
        middle_layout.addWidget(self.detail_table_view)
        middle_layout.addWidget(self.file_list_view)
        layout.addWidget(self.middle_container, 7)

        # 详情区
        self.detail_panel = DetailPanel(self)
        layout.addWidget(self.detail_panel, 3)

        self.setCentralWidget(central_widget)

        # 连接信号
        self.file_list_view.itemSelectionChanged.connect(self._on_selection_changed)
        self.detail_table_view.itemSelectionChanged.connect(self._on_selection_changed)
        self.detail_panel.tags_changed.connect(self._on_tags_changed)
        self.detail_table_view.refresh()  # 初始化时刷新详情表格
        self.file_list_view.refresh()  # 初始化时刷新文件列表
        self.detail_table_view.delete_requested.connect(self._on_delete_images)
        self.detail_table_view.copy_path_requested.connect(self._on_copy_paths)
        self.detail_table_view.reveal_requested.connect(self._on_reveal_files)
        self.detail_table_view.reconnect_requested.connect(self._on_reconnect_files)
        self.file_list_view.delete_requested.connect(self._on_delete_images)
        self.file_list_view.copy_path_requested.connect(self._on_copy_paths)
        self.file_list_view.reveal_requested.connect(self._on_reveal_files)
        self.file_list_view.reconnect_requested.connect(self._on_reconnect_files)
        self.toolbar.search_input.textChanged.connect(self._on_search_changed)
        self.toolbar.view_group.buttonClicked.connect(self._on_view_changed)
        self.toolbar.refresh_button.clicked.connect(self._on_refresh_clicked)
        self.toolbar.export_button.clicked.connect(self._on_export_clicked)
        self.toolbar.restore_button.clicked.connect(self._on_restore_clicked)

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

    def _on_export_clicked(self):
        """处理导出数据库备份的请求。"""
        path, _ = QFileDialog.getSaveFileName(
            self, "导出数据库备份", "pictaggerbackup.db",
            filter="数据库文件 (*.db)"
        )
        if path:
            backup_service.backup(path)
            QMessageBox.information(self, "导出完成", f"数据库备份已导出到: {path}")

    def _on_refresh_clicked(self):
        """处理刷新按钮点击事件。"""
        missing = image_service.check_missing_files()
        self._refresh_all()
        if missing:
            QMessageBox.information(self, "刷新完成", f"检测到 {missing} 张图片文件丢失。")
        logger.info(f"刷新完成: 检测到 {missing} 张图片文件丢失。")

    def _on_view_changed(self, button):
        """处理视图切换的请求。

        :param button: 被点击的按钮
        """
        index = self.toolbar.view_buttons.index(button)
        if index == 4: # 详情列表
            self.file_list_view.hide()
            self.detail_table_view.show()
        else:
            # 超大/大/中/小图标
            sizes = [256, 128, 64, 48]
            self.file_list_view.set_icon_size(sizes[index])
            self.detail_table_view.hide()
            self.file_list_view.show()

    def _on_search_changed(self, keyword: str):
        """处理搜索输入框文本变化的请求。

        :param keyword: 搜索关键字
        """
        keyword = keyword.strip()
        if keyword:
            images = search_service.search_image_by_keyword(keyword)
        else:
            images = None

        # 根据关键字搜索图片
        self.file_list_view.refresh(images)
        self.detail_table_view.refresh(images)

    def _on_copy_paths(self, image_ids: list[int]):
        """处理复制图片路径的请求。

        :param image_ids: 要复制路径的图片 ID 列表
        """
        if not image_ids:
            return
        paths = []
        for image_id in image_ids:
            image = image_service.get_image_by_id(image_id)
            if image:
                paths.append(image.file_path)
        if paths:
            QGuiApplication.clipboard().setText("\n".join(paths))
            logger.info(f"复制图片路径: {len(paths)} 个路径已复制到剪贴板")

    def _on_reveal_files(self, image_ids: list[int]):
        """在文件管理器中定位文件"""
        if not image_ids:
            return
        for image_id in image_ids:
            image = image_service.get_image_by_id(image_id)
            if image and Path(image.file_path).exists():
                self._reveal_in_file_manager(image.file_path)

    def _reveal_in_file_manager(self, file_path: str):
        """在文件管理器中定位文件。

        :param file_path: 文件路径
        """
        path = Path(file_path)
        if os.name == "nt": # Windows
            subprocess.Popen(["explorer", "/select,", str(path)])
        elif sys.platform == "darwin": # macOS
            subprocess.Popen(["open", "-R", str(path)])
        else: # Linux
            subprocess.Popen(["xdg-open", str(path.parent)])

    def _on_reconnect_files(self, image_ids: list[int]):
        """处理重新连接文件的请求。

        :param image_ids: 要重新连接的图片 ID 列表
        """
        if not image_ids:
            return
        for image_id in image_ids:
            image = image_service.get_image_by_id(image_id)
            if not image:
                return
            path, _ = QFileDialog.getOpenFileName(
                self, "选择新的图片文件",
                str(Path(image.file_path).parent),
                filter=f"图片文件 ({'*'+' *'.join(self.import_controller.IMAGE_EXTENSIONS)})"
            )
            if not path:
                continue
            try:
                image_service.reconnect_image(image_id, Path(path))
            except Exception as e:
                logger.error(f"重新连接图片失败: image_id={image_id}, new_path={path}, 错误: {e}")
                QMessageBox.critical(self, "重新连接失败", f"无法重新连接图片文件: {e}")
                return
            logger.info(f"重新连接图片: image_id={image_id}, new_path={path}")
        self._refresh_all()
        self._on_selection_changed()  # 更新详情面板显示

    def _refresh_all(self):
        """刷新文件列表和详情表格。"""
        self.file_list_view.refresh()
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
        self.file_list_view.refresh()

    def _on_selection_changed(self):
        """当选中图片发生变化时，更新详情面板的显示。"""
        # 根据当前激活的视图获取选中项
        if not self.file_list_view.isHidden():
            # 图标视图（超大/大/中/小）
            selected = self.file_list_view.selectedItems()
            if not selected:
                self.detail_panel.clear()
                return
            ids = [item.data(Qt.ItemDataRole.UserRole) for item in selected]
        else:
            # 详情表格视图
            selected = self.detail_table_view.selectedItems()
            if not selected:
                self.detail_panel.clear()
                return
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

    def _on_restore_clicked(self):
        """处理恢复数据库备份的请求。"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择备份文件", "",
            filter="数据库文件 (*.db)"
        )
        if not path:
            return
        # 确认恢复（会覆盖当前数据）
        reply = QMessageBox.question(
            self, "确认恢复",
            "恢复备份将覆盖当前所有数据，确定继续吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            backup_service.restore(path)
        except Exception as e:
            logger.error(f"恢复数据库失败: {e}")
            QMessageBox.critical(self, "恢复失败", f"无法恢复数据库: {e}")
            return
        # 恢复后刷新所有视图
        self._refresh_all()
        self.detail_panel.clear()
        # 重新生成缺失的缩略图
        regenerated = image_service.regenerate_missing_thumbnails()
        if regenerated:
            self._refresh_all()  # 重新生成后再次刷新
        QMessageBox.information(self, "恢复完成", f"数据库已从备份恢复。重新生成 {regenerated} 张缩略图。")
        logger.info(f"数据库恢复完成: {path}")