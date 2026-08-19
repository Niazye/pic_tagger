from src.database import get_connection
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt6.QtCore import Qt
from src.views.main_window import MainWindow
from src.utils.logger import setup_logging
import sys
def create_app() -> QApplication:
    """
    创建并返回一个 PyQt6 应用实例。

    :return: QApplication 实例
    """
    setup_logging()  # 设置日志记录
    get_connection()  # 确保数据库连接已建立
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(800, 600)
    window.setWindowFlag(window.windowFlags() | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint)

    window.showMaximized()
    app._main_window = window  # 将主窗口设置为应用的属性，便于在其他地方访问
    return app

def main():
    app = create_app()
    sys.exit(app.exec())
