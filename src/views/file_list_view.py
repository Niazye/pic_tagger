from PyQt6.QtWidgets import QListWidget, QMainWindow, QListWidgetItem, QMenu
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from src.services import thumbnail_service, image_service
from src.models import Image
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FileListView(QListWidget):
    # 右键菜单信号
    delete_requested = pyqtSignal(list)  # 删除
    copy_path_requested = pyqtSignal(list)  # 复制路径
    reveal_requested = pyqtSignal(list)  # 显示在文件夹中
    reconnect_requested = pyqtSignal(list)  # 重新连接

    def __init__(self, parent: QMainWindow | None = None):
        super().__init__(parent)
        self.setViewMode(QListWidget.ViewMode.IconMode)  # 设置为图标模式
        self.setIconSize(QSize(128, 128))  # 设置图标大小
        self.setGridSize(QSize(160, 180))  # 设置网格大小
        self.setResizeMode(QListWidget.ResizeMode.Adjust)  # 自动调整大小
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # 支持多选
        self.setWordWrap(True)  # 启用文字换行
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # 启用自定义右键菜单
        self.customContextMenuRequested.connect(self._show_context_menu)  # 连接右键菜单信号

    def refresh(self, images: list[Image] | None = None) -> None:
        """刷新文件列表视图。

        :param images: 要显示的图片列表；为 None 时显示全部图片
        """
        self.clear()  # 清空当前列表
        if images is None:
            images = image_service.get_all_images()
        for image in images:
            self.add_image_item(image)
        logger.debug(f"刷新文件列表: 共 {len(images)} 张图片")

    def set_icon_size(self, size: int) -> None:
        """设置图标大小, 并相应地调整网格大小。

        :param size: 图标的宽度和高度（正方形）
        """
        self.setIconSize(QSize(size, size))
        # 网格比图标稍大，以便显示文件名
        self.setGridSize(QSize(size + 32, size + 52))

    def add_image_item(self, image: Image) -> None:
        """向列表中添加一个图片项。"""
        item = QListWidgetItem(image.file_name)
        item.setText(image.file_name)
        item.setData(Qt.ItemDataRole.UserRole, image.id)
        item.setIcon(self._load_thumbnail(image))
        if image.is_missing:
            item.setText(f"⚠ {image.file_name}")
            item.setForeground(Qt.GlobalColor.gray)
        self.addItem(item)

    def _load_thumbnail(self, image: Image) -> QIcon:
        """加载并设置图片的缩略图。"""
        thumbnail_path = thumbnail_service.get_thumbnail_path(image.id)
        if not thumbnail_path.exists():
            thumbnail_path = thumbnail_service.get_default_thumbnail_path()
        pixmap = QPixmap(str(thumbnail_path))
        if pixmap.isNull():
            logger.warning(f"加载缩略图失败: image_id={image.id}, path={thumbnail_path}")
            return QIcon()
        return QIcon(pixmap)

    def _show_context_menu(self, position):
        """显示右键菜单。"""
        item = self.itemAt(position)
        if item is None:
            return  # 如果没有选中项，则不显示菜单

        if not item.isSelected():
            self.clearSelection()
            item.setSelected(True)

        menu = QMenu(self)
        delete_action = menu.addAction("删除索引")
        copy_action = menu.addAction("复制路径")
        reveal_action = menu.addAction("在文件管理器中定位")
        reconnect_action = menu.addAction("重新连接文件")

        selected = self.selectedItems()
        ids = [i.data(Qt.ItemDataRole.UserRole) for i in selected]

        action = menu.exec(self.mapToGlobal(position))
        if action == delete_action:
            self.delete_requested.emit(ids)
        elif action == copy_action:
            self.copy_path_requested.emit(ids)
        elif action == reveal_action:
            self.reveal_requested.emit(ids)
        elif action == reconnect_action:
            self.reconnect_requested.emit(ids)