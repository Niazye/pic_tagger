from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QPushButton, QLineEdit, QMessageBox, QDialogButtonBox, QListWidgetItem, QInputDialog
from src.utils.logger import get_logger
from src.services import category_service, tag_service

logger = get_logger(__name__)

class TagDialog(QDialog):
    """标签对话框，用于创建或编辑标签。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("标签管理")
        self.setMinimumWidth(420)
        self.setMinimumHeight(400)
        self._build_ui()
        self._load_categories()
        self._load_tags()

    def _build_ui(self) -> None:
        """构建"""
        layout = QVBoxLayout(self)

        # 分类选择
        cat_row = QHBoxLayout(self)
        cat_row.addWidget(QLabel("选择分类:"))
        self.category_combo = QComboBox(self)
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        cat_row.addWidget(self.category_combo, 1)
        layout.addLayout(cat_row)

        # 标签列表
        layout.addWidget(QLabel("标签列表:"))
        self.tag_list = QListWidget()
        self.tag_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.tag_list, 1)

        # 新建标签
        create_frame = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("新标签名称")
        create_frame.addWidget(self.name_input, 1)

        self.create_btn = QPushButton("创建标签")
        self.create_btn.clicked.connect(self._on_create)
        create_frame.addWidget(self.create_btn)
        layout.addLayout(create_frame)

        # 操作按钮
        btn_row = QHBoxLayout()
        self.rename_btn = QPushButton("重命名")
        self.rename_btn.clicked.connect(self._on_rename)
        self.rename_btn.setEnabled(False)
        btn_row.addWidget(self.rename_btn)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.clicked.connect(self._on_delete)
        self.delete_btn.setEnabled(False)
        btn_row.addWidget(self.delete_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        # 关闭按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _load_categories(self) -> None:
        """加载分类到下拉框。"""
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        categories = category_service.get_all_categories()
        for category in categories:
            self.category_combo.addItem(category.name, category.id)
        self.category_combo.blockSignals(False)

    def _load_tags(self) -> None:
        """加载当前选中分类的标签到列表。"""
        self.tag_list.clear()
        category_id = self.category_combo.currentData()
        if category_id is None:
            return
        tags = tag_service.get_all_tags_by_category(category_id)
        for tag in tags:
            item = QListWidgetItem(tag.name)
            item.setData(0x0100, tag.id)  # Qt.UserRole = 0x0100
            self.tag_list.addItem(item)

    def _selected_tag_id(self) -> int | None:
        """获取当前选中标签的 ID。"""
        item = self.tag_list.currentItem()
        if not item:
            return None
        return item.data(0x0100)  # Qt.UserRole = 0x0100

    def _on_category_changed(self) -> None:
        """当分类选择改变时，重新加载标签列表。"""
        self._load_tags()

    def _on_selection_changed(self) -> None:
        """当标签选择改变时，更新按钮状态。"""
        has_selection = self._selected_tag_id() is not None
        self.rename_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def _on_create(self) -> None:
        """创建新标签。"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "错误", "标签名称不能为空。")
            return

        category_id = self.category_combo.currentData()
        if category_id is None:
            return

        # 检查标签是否已存在
        existing = next((t for t in tag_service.get_all_tags_by_category(category_id) if t.name == name), None)

        if existing:
            QMessageBox.warning(self, "错误", f"标签 '{name}' 已存在。")
            return
        try:
            tag_service.add_tag(category_id, name)
        except Exception as e:
            logger.error(f"创建标签失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"创建标签失败: {e}")
            return
        self.name_input.clear()
        self._load_tags()
        logger.info(f"创建标签: {name} (分类 ID: {category_id})")

    def _on_rename(self) -> None:
        """重命名选中的标签。"""
        tag_id = self._selected_tag_id()
        if tag_id is None:
            return
        category_id = self.category_combo.currentData()
        tags = tag_service.get_all_tags_by_category(category_id)
        current = next((t for t in tags if t.id == tag_id), None)
        if not current:
            return
        new_name, ok = QInputDialog.getText(self, "重命名标签", "新标签名称:")
        if not ok or not new_name.strip():
            return
        # 检查标签是否已存在
        existing = next((t for t in tag_service.get_all_tags_by_category(category_id) if t.name == new_name), None)
        if existing:
            QMessageBox.warning(self, "错误", f"标签 '{new_name}' 已存在。")
            return
        try:
            tag_service.rename_tag(tag_id, new_name.strip())
        except Exception as e:
            logger.error(f"重命名标签失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"重命名标签失败: {e}")
            return
        self._load_tags()
        logger.info(f"重命名标签: id={tag_id}, 新名称={new_name.strip()}")

    def _on_delete(self) -> None:
        """删除选中的标签。"""
        tag_id = self._selected_tag_id()
        if tag_id is None:
            return
        category_id = self.category_combo.currentData()
        tags = tag_service.get_all_tags_by_category(category_id)
        current = next((t for t in tags if t.id == tag_id), None)
        if not current:
            return
        
        reply = QMessageBox.question(self, "确认删除", f"确定要删除标签「{current.name}」吗？\n该操作会同时移除所有图片上的此标签。", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            tag_service.delete_tag(tag_id)
        except Exception as e:
            logger.error(f"删除标签失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"删除标签失败: {e}")
            return
        self._load_tags()
        logger.info(f"删除标签: id={tag_id}")