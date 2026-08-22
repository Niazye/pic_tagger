from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMainWindow, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from src.services import image_service, category_service, image_tag_service
from src.models import Image, Category
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.format import *

logger = get_logger(__name__)

class _NumericItem(QTableWidgetItem):
    """自定义的 QTableWidgetItem，用于支持数值排序。"""

    def __init__(self, text: str, value: float):
        super().__init__(text)
        self._value = value
    def __lt__(self, other: QTableWidgetItem) -> bool:
        """重写小于运算符以支持数值排序。"""
        if isinstance(other, _NumericItem):
            return self._value < other._value
        return super().__lt__(other)

class DetailTableView(QTableWidget):
    BASE_COLUMNS = ["文件名", "大小", "尺寸", "修改时间", "导入时间"]

    # 右键菜单信号
    delete_requested = pyqtSignal(list)  # 删除
    copy_path_requested = pyqtSignal(list)  # 复制路径
    reveal_requested = pyqtSignal(list)  # 显示在文件夹中
    reconnect_requested = pyqtSignal(list)  # 重新连接

    def __init__(self, parent: QMainWindow | None = None):
        super().__init__(parent)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.setSortingEnabled(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def refresh(self, images: list[Image] | None = None) -> None:
        if images is None:
            images = image_service.get_all_images()
        categories = category_service.get_all_categories()

        category_columns = [c.name for c in categories]
        all_columns = self.BASE_COLUMNS + category_columns

        # 填充数据前，先禁用排序以避免性能问题
        self.setSortingEnabled(False)

        self.setColumnCount(len(all_columns))
        self.setHorizontalHeaderLabels(all_columns)
        self.setRowCount(len(images))

        for row, image in enumerate(images):
            self._populate_row(row, image, categories)

        self.resizeColumnsToContents()

        # 重新启用排序
        self.setSortingEnabled(True)
        logger.debug(f"刷新详细信息表格: 共 {len(images)} 张图片, {len(categories)} 个分类")

    def _show_context_menu(self, pos) -> None:
        """显示右键菜单。"""
        item = self.itemAt(pos)
        if not item:
            return
        # 确保右键点击的行被选中
        if not item.isSelected():
            self.clearSelection()
            item.setSelected(True)

        menu = QMenu(self)
        delete_action = menu.addAction("删除索引")
        copy_action = menu.addAction("复制路径")
        reveal_action = menu.addAction("在文件管理器中定位")
        reconnect_action = menu.addAction("重新连接文件")

        # 获取选中行的图片 ID
        rows = set()
        for selected_item in self.selectedItems():
            rows.add(selected_item.row())
        ids = []
        for row in rows:
            name_item = self.item(row, 0)
            if name_item:
                image_id = name_item.data(Qt.ItemDataRole.UserRole)
                if image_id is not None:
                    ids.append(image_id)

        action = menu.exec(self.mapToGlobal(pos))
        if action == delete_action:
            self.delete_requested.emit(ids)
        elif action == copy_action:
            self.copy_path_requested.emit(ids)
        elif action == reveal_action:
            self.reveal_requested.emit(ids)
        elif action == reconnect_action:
            self.reconnect_requested.emit(ids)


    def _populate_row(self, row: int, image: Image, categories: list[Category]) -> None:
        # 文件名
        name_item = QTableWidgetItem(image.file_name or image.file_path)
        name_item.setData(Qt.ItemDataRole.UserRole, image.id)  # 将图片 ID 存储在 UserRole 中，便于后续操作
        if image.is_missing:
            name_item.setText(f"⚠ {image.file_name or image.file_path}")
            name_item.setForeground(Qt.GlobalColor.gray)
        self.setItem(row, 0, name_item)

        # 大小
        size_text = format_size(image.file_size)
        self.setItem(row, 1, _NumericItem(size_text, image.file_size or 0))

        # 尺寸
        dim_text = format_dimension(image.width, image.height)
        area = (image.width or 0) * (image.height or 0)
        self.setItem(row, 2, _NumericItem(dim_text, area))

        # 修改时间
        mtime_text = format_datetime(image.file_mtime)
        self.setItem(row, 3, QTableWidgetItem(mtime_text))

        # 导入时间
        ctime_text = format_datetime(image.created_at)
        self.setItem(row, 4, QTableWidgetItem(ctime_text))

        grouped_tags = image_tag_service.get_image_tags_grouped_by_category(image.id)
        for col, category in enumerate(categories, start = len(self.BASE_COLUMNS)):
            tags = grouped_tags.get(category.id, [])
            tag_text = "、".join(tag.name for tag in tags) if tags else ""
            self.setItem(row, col, QTableWidgetItem(tag_text))
