from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMainWindow
from src.services import image_service, category_service, image_tag_service
from src.models import Image, Category
from datetime import datetime

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
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__(parent)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.setSortingEnabled(True)

    def refresh(self) -> None:
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

    def _populate_row(self, row: int, image: Image, categories: list[Category]) -> None:
        # 文件名
        self.setItem(row, 0, QTableWidgetItem(image.file_name or image.file_path))

        # 大小
        size_text = self._format_size(image.file_size)
        self.setItem(row, 1, _NumericItem(size_text, image.file_size or 0))

        # 尺寸
        dim_text = f"{image.width}×{image.height}" if image.width and image.height else "未知"
        area = (image.width or 0) * (image.height or 0)
        self.setItem(row, 2, _NumericItem(dim_text, area))

        # 修改时间
        mtime_text = self._format_datetime(image.file_mtime)
        self.setItem(row, 3, QTableWidgetItem(mtime_text))

        # 导入时间
        ctime_text = self._format_datetime(image.created_at)
        self.setItem(row, 4, QTableWidgetItem(ctime_text))

        grouped_tags = image_tag_service.get_image_tags_grouped_by_category(image.id)
        for col, category in enumerate(categories, start = len(self.BASE_COLUMNS)):
            tags = grouped_tags.get(category.id, [])
            tag_text = "、".join(tag.name for tag in tags) if tags else ""
            self.setItem(row, col, QTableWidgetItem(tag_text))

    def _format_size(self, size: int | None) -> str:
        if not size:
            return ""
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.1f} MB"

    def _format_datetime(self, dt: datetime | None) -> str:
        if not dt:
            return ""
        return dt.strftime("%Y-%m-%d %H:%M")