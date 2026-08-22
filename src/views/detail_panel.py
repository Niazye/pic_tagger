from src.utils.logger import get_logger
from src.utils.format import *
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QTextEdit, QComboBox, QLineEdit, QPushButton
from src.models import Image, Tag
from src.services import thumbnail_service, category_service, image_tag_service, image_service, tag_service


logger = get_logger(__name__)


class DetailPanel(QWidget):
    """右侧详情面板。

    显示选中图片的缩略图、基础信息、描述编辑区和标签编辑区。
    支持单图模式和多选模式。
    """

    tags_changed = pyqtSignal()

    def __init__(self, parent: QMainWindow | None = None):
        super().__init__(parent)
        self._current_image: Image | None = None
        self._selected_ids: list[int] = []
        self._build_ui()

    def _build_ui(self) -> None:
        """构建界面。"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 缩略图预览
        self.preview_label = QLabel("未选择图片")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc;"
        )
        layout.addWidget(self.preview_label)

        # 文件基础信息
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(4)
        self.info_labels: dict[str, QLabel] = {}
        for key, label in [
            ("path", "路径"),
            ("size", "大小"),
            ("dimension", "尺寸"),
            ("mtime", "修改时间"),
            ("ctime", "导入时间"),
        ]:
            row = QHBoxLayout()
            title = QLabel(f"{label}:")
            title.setFixedWidth(60)
            value = QLabel("-")
            value.setWordWrap(True)
            row.addWidget(title)
            row.addWidget(value, 1)
            info_layout.addLayout(row)
            self.info_labels[key] = value
        layout.addWidget(info_frame)

        # 描述编辑区
        desc_label = QLabel("描述:")
        layout.addWidget(desc_label)
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("输入描述，自动保存...")
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.textChanged.connect(self._on_desc_changed)
        layout.addWidget(self.desc_edit)

        # 标签编辑区
        tag_label = QLabel("标签:")
        layout.addWidget(tag_label)

        # 分类下拉框 + 标签输入框
        tag_input_row = QHBoxLayout()
        self.category_combo = QComboBox()
        tag_input_row.addWidget(self.category_combo, 1)

        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("输入标签，回车添加")
        self.tag_input.returnPressed.connect(self._on_add_tag)
        tag_input_row.addWidget(self.tag_input, 2)

        layout.addLayout(tag_input_row)

        # 已挂载标签列表（药丸样式）
        self.tags_container = QWidget()
        self.tags_layout = QVBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(4)
        self.tags_layout.addStretch()
        layout.addWidget(self.tags_container)

        layout.addStretch()

    # ---- 对外接口 ----

    def show_image(self, image: Image) -> None:
        """显示指定图片的详细信息。

        :param image: 要显示的图片对象
        """
        self._current_image = image
        self._selected_ids = [image.id]
        self._update_preview(image)
        self._update_info(image)
        self._update_desc(image)
        self._update_categories()
        self._update_tags()

    def show_multi(self, image_ids: list[int]) -> None:
        """显示多选图片的详细信息。
        
        :param image_ids: 要显示的图片ID列表
        """
        self._current_image = None
        self._selected_ids = image_ids
        self.preview_label.setText(f"已选中 {len(image_ids)} 张图片")
        self.preview_label.setPixmap(QPixmap())
        for key in self.info_labels:
            self.info_labels[key].setText("-")
        self.desc_edit.blockSignals(True)
        self.desc_edit.clear()
        self.desc_edit.blockSignals(False)
        self._update_categories()
        self._update_tags()

    def clear(self) -> None:
        """清空详情面板。"""
        self._current_image = None
        self._selected_ids = []
        self.preview_label.setText("未选择图片")
        self.preview_label.setPixmap(QPixmap())
        for key in self.info_labels:
            self.info_labels[key].setText("-")
        self.desc_edit.blockSignals(True)
        self.desc_edit.clear()
        self.desc_edit.blockSignals(False)
        self._clear_tags()

    # ---- 内部方法 ----

    def _update_preview(self, image: Image) -> None:
        """更新缩略图预览。"""
        thumbnail_path = thumbnail_service.get_thumbnail_path(image.id)
        if not thumbnail_path.exists():
            thumbnail_path = thumbnail_service.get_default_thumbnail_path()
        pixmap = QPixmap(str(thumbnail_path))
        if pixmap.isNull():
            self.preview_label.setText("无法加载预览")
            self.preview_label.setPixmap(QPixmap())
            return

        # 缩放适配面板
        scaled = pixmap.scaled(
            self.preview_label.width(), 300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)

    def _update_info(self, image: Image) -> None:
        """更新文件基础信息。"""
        self.info_labels["path"].setText(image.file_path)
        self.info_labels["size"].setText(format_size(image.file_size))
        self.info_labels["dimension"].setText(format_dimension(image.width, image.height))
        self.info_labels["mtime"].setText(format_datetime(image.file_mtime))
        self.info_labels["ctime"].setText(format_datetime(image.created_at))

    def _update_desc(self, image: Image) -> None:
        """更新描述编辑区。"""
        self.desc_edit.blockSignals(True)
        self.desc_edit.setPlainText(image.description or "")
        self.desc_edit.blockSignals(False)

    def _update_categories(self) -> None:
        """更新分类下拉框。"""
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        categories = category_service.get_all_categories()
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
        self.category_combo.blockSignals(False)

    def _update_tags(self) -> None:
        """更新已挂载标签列表。"""
        self._clear_tags()
        if not self._selected_ids:
            return
        # 单图模式：显示该图片的标签
        if self._current_image is not None:
            grouped = image_tag_service.get_image_tags_grouped_by_category(self._current_image.id)
            for category in category_service.get_all_categories():
                for tag in grouped.get(category.id, []):
                    self._add_tag_pill(category.name, tag.name, tag.id)
        # 多选模式：显示所有选中图片的公共标签
        else:
            common_tags: dict[int, list[Tag]] = {}
            for idx, image_id in enumerate(self._selected_ids):
                grouped = image_tag_service.get_image_tags_grouped_by_category(image_id)
                if idx == 0:
                    common_tags = {cat_id: tags.copy() for cat_id, tags in grouped.items()}
                else:
                    # 取交集
                    for cat_id in list(common_tags.keys()):
                        current = {t.id for t in grouped.get(cat_id, [])}
                        common_tags[cat_id] = [t for t in common_tags[cat_id] if t.id in current]
            for category in category_service.get_all_categories():
                for tag in common_tags.get(category.id, []):
                    self._add_tag_pill(category.name, tag.name, tag.id)

    def _add_tag_pill(self, category_name: str, tag_name: str, tag_id: int) -> None:
        """添加一个标签药丸。"""
        pill = QFrame()
        pill.setStyleSheet(
            "QFrame { background-color: #e0e0e0; border-radius: 10px; padding: 2px 8px; }"
        )
        row = QHBoxLayout(pill)
        row.setContentsMargins(4, 2, 4, 2)
        row.setSpacing(4)
        label = QLabel(f"{category_name}: {tag_name}")
        row.addWidget(label)
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet("border: none; background: transparent;")
        remove_btn.clicked.connect(lambda: self._on_remove_tag(tag_id))
        row.addWidget(remove_btn)
        self.tags_layout.insertWidget(self.tags_layout.count() - 1, pill)

    def _clear_tags(self) -> None:
        """清空标签列表。"""
        while self.tags_layout.count() > 1:
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _on_desc_changed(self) -> None:
        """描述变更时自动保存。"""
        if self._current_image is None:
            return
        desc = self.desc_edit.toPlainText()
        image_service.update_description(self._current_image.id, desc)

    def _on_add_tag(self) -> None:
        """添加标签。"""
        if not self._selected_ids:
            return
        name = self.tag_input.text().strip()
        if not name:
            return
        category_id = self.category_combo.currentData()
        if category_id is None:
            return
        # 查找或创建标签
        existing = next(
            (t for t in tag_service.get_all_tags_by_category(category_id) if t.name == name),
            None,
        )
        if existing is None:
            existing = tag_service.add_tag(category_id, name)
        # 为所有选中图片添加标签
        for image_id in self._selected_ids:
            image_tag_service.add_tag_to_image(image_id, existing.id)
        self.tag_input.clear()
        self._update_tags()
        self.tags_changed.emit()
        logger.info(f"添加标签: tag={name}, category_id={category_id}, images={self._selected_ids}")

    def _on_remove_tag(self, tag_id: int) -> None:
        """移除标签。"""
        if not self._selected_ids:
            return
        image_tag_service.batch_remove_tag_from_images(self._selected_ids, tag_id)
        self._update_tags()
        self.tags_changed.emit()
        logger.info(f"移除标签: tag_id={tag_id}, images={self._selected_ids}")

