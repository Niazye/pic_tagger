from src.utils.logger import get_logger
from src.utils.exception import DefaultCategoryError
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QListWidget, QDialogButtonBox, QListWidgetItem, QMessageBox, QInputDialog
from src.services import category_service, tag_service
from src.database import DEFAULT_CATEGORY_ID

logger = get_logger(__name__)

# 分类类型选项
CATEGORY_TYPES = [
    ("free", "自由式（可自由输入新标签）"),
    ("option", "选项式（只能从已有标签中选择）"),
    ("unique", "唯一式（每张图片该分类下只能有一个标签）"),
]

class CategoryDialog(QDialog):
    """分类管理对话框。

    集中处理分类的创建、重命名、删除。
    默认分类（未分类）不允许重命名和删除。
    """
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("分类管理")
        self.setMinimumWidth(420)
        self.setMinimumHeight(400)
        self._build_ui()
        self._load_categories()

    def _build_ui(self) -> None:
        """构建界面。"""
        layout = QVBoxLayout(self)

        # 分类列表
        layout.addWidget(QLabel("分类列表："))
        self.category_list = QListWidget()
        self.category_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.category_list, 1)

        # 新建分类区
        create_frame = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("新分类名称")
        create_frame.addWidget(self.name_input, 2)

        self.type_combo = QComboBox()
        for value, display in CATEGORY_TYPES:
            self.type_combo.addItem(display, value)
        create_frame.addWidget(self.type_combo, 3)
        
        self.create_btn = QPushButton("创建")
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
        """加载分类列表。"""
        self.category_list.clear()
        categories = category_service.get_all_categories()
        for category in categories:
            item = QListWidgetItem(category.name)
            item.setData(0x0100, category.id)
            # 默认分类（未分类）不允许重命名和删除
            if category.id == DEFAULT_CATEGORY_ID:
                item.setText(f"{category.name} (默认分类)")
            self.category_list.addItem(item)

    def _selected_category_id(self) -> int | None:
        """获取当前选中的分类 ID，如果没有选中则返回 None。"""
        selected_items = self.category_list.currentItem()
        if not selected_items:
            return None
        return selected_items.data(0x0100)

    def _on_selection_changed(self):
        """当选中分类发生变化时，更新按钮状态。"""
        category_id = self._selected_category_id()
        is_default = category_id == DEFAULT_CATEGORY_ID
        self.rename_btn.setEnabled(category_id is not None and not is_default)
        self.delete_btn.setEnabled(category_id is not None and not is_default)

    def _on_create(self):
        """处理创建分类的逻辑。"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "分类名称不能为空！")
            return
        type_value = self.type_combo.currentData()
        try:
            category_service.create_category(name, type_value)
        except Exception as e:
            logger.error(f"创建分类失败: name={name}, type={type_value}, 错误: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"创建分类失败: {e}")
            return
        self.name_input.clear()
        self._load_categories()
        logger.info(f"创建分类成功: name={name}, type={type_value}")

    def _on_rename(self):
        """处理重命名分类的逻辑。"""
        category_id = self._selected_category_id()
        if category_id is None:
            return
        categories = category_service.get_all_categories()
        current = next((c for c in categories if c.id == category_id), None)
        if not current:
            QMessageBox.warning(self, "警告", "选中的分类不存在！")
            return
        new_name, ok = QInputDialog.getText(self, "重命名分类", "输入新的分类名称：", text=current.name)
        if not ok or not new_name.strip():
            return
        try:
            category_service.rename_category(category_id, new_name.strip())
        except DefaultCategoryError as e:
            QMessageBox.warning(self, "提示", str(e))
            return
        except Exception as e:
            logger.error(f"重命名分类失败: id={category_id}, new_name={new_name}, 错误: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"重命名分类失败: {e}")
            return
        self._load_categories()
        logger.info(f"重命名分类成功: id={category_id}, new_name={new_name}")

    def _on_delete(self):
        """处理删除分类的逻辑。"""
        category_id = self._selected_category_id()
        if category_id is None:
            return
        categories = category_service.get_all_categories()
        current = next((c for c in categories if c.id == category_id), None)
        if not current:
            QMessageBox.warning(self, "警告", "选中的分类不存在！")
            return

        # 检查是否有标签属于该分类
        tags = tag_service.get_all_tags_by_category(category_id)
        if tags:
            # 非空分类：二选一
            choice = QMessageBox.question(
                self,
                "删除分类",
                f"分类「{current.name}」下有 {len(tags)} 个标签。\n"
                "选择「是」迁移标签到默认分类，选择「否」删除所有标签。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if choice == QMessageBox.StandardButton.Cancel:
                return
            mode = "move_to_default" if choice == QMessageBox.StandardButton.Yes else "delete_tags"
        else:
            # 空
            mode = "move_to_default"  # 默认模式
        try:
            category_service.delete_category(category_id, mode)
        except DefaultCategoryError as e:
            QMessageBox.warning(self, "提示", str(e))
            return
        except Exception as e:
            logger.error(f"删除分类失败: id={category_id}, 错误: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"删除分类失败: {e}")
            return
        self._load_categories()
        logger.info(f"删除分类成功: id={category_id}")
