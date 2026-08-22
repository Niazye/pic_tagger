from PyQt6.QtWidgets import QToolBar, QLineEdit, QPushButton, QHBoxLayout, QWidget, QButtonGroup, QMainWindow
class ToolBar(QToolBar):
    def __init__(self, parent: QMainWindow | None = None):
        super().__init__("主工具栏", parent)
        self.setMovable(False)  # 禁止工具栏移动
        self.setFloatable(False)  # 禁止工具栏浮动
        self.setStyleSheet("background-color: #f0f0f0;")  # 设置工具栏背景颜色

        # 添加全局搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("全局搜索")
        self.search_input.setClearButtonEnabled(True)  # 启用清除按钮
        self.search_input.setFixedWidth(200)  # 设置输入框宽度
        self.addWidget(self.search_input)

        self.addSeparator()  # 添加分隔符

        # 添加视图切换按钮
        self.view_group = QButtonGroup(self)
        self.view_buttons = []
        for label in ["超大", "大", "中", "小", "详情列表"]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            self.view_group.addButton(btn)
            self.view_buttons.append(btn)
            self.addWidget(btn)
        if self.view_buttons:
            self.view_buttons[-1].setChecked(True)  # 默认选中“详情列表”按钮

        self.addSeparator()  # 添加分隔符

        # 添加刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.addWidget(self.refresh_button)

        # 添加导入按钮
        self.import_button = QPushButton("导入")
        self.addWidget(self.import_button)

        # 添加导出按钮
        self.export_button = QPushButton("导出")
        self.addWidget(self.export_button)

        # 添加恢复按钮
        self.restore_button = QPushButton("恢复")
        self.addWidget(self.restore_button)
